"""Проверяем упаковку курса без моделей и без сети.

Ссылки и пунктуация в Markdown, совпадение архивов с папками exercises и skills, этапы скилла
в каркасах и скрипты проверки на JavaScript и Python. Успех не означает, что ученик прошёл уроки
или что модель выполняет правила скилла: это видно только по настоящим ответам в OpenCode.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'tools' / 'course-map.json').read_text(encoding='utf-8'))
SKIP = ('.git', '.checks')
TEXT = ('.md', '.py', '.js', '.json', '.txt', '.html', '.csv', '.gitignore')
SAMPLES = {
    'story': ('Ему стало грустно. Сердце сжалось.\n', 'Ильич вскрыл конверт и узнал почерк Нины.\n'),
    'spec': ('Сайт удобный и т.д.\n', 'Доставка по городу бесплатная.\n'),
    'translation': ('Возьмите токен, это твой ход.\n', 'Если масло закончилось, пропустите два следующих хода.\n'),
}


def check_markdown() -> tuple[int, int]:
    files = [path for path in ROOT.rglob('*.md') if not any(part in SKIP for part in path.relative_to(ROOT).parts)]
    links = 0
    for path in files:
        text = path.read_text(encoding='utf-8')
        special = sorted({char for char in text if ord(char) > 127 and unicodedata.category(char)[0] in 'PSZ'})
        assert not special, (path, 'Только клавиатурная пунктуация', special)
        assert not re.search(r'\[\[[^\]\n]+\]\]', text), (path, 'Осталась ссылка Obsidian')
        assert text.count('```') % 2 == 0, (path, 'Незакрытый блок кода')
        # Ссылки внутри кода - это примеры для читателя, а не переходы по курсу.
        prose = re.sub(r'`[^`\n]*`', '', re.sub(r'```.*?```', '', text, flags=re.S))
        targets = re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', prose) + re.findall(r'<img[^>]+src="([^"]+)"', prose)
        for target in targets:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / unquote(url.path)).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), (path, target)
            links += 1
    return len(files), links


def normalized(data: bytes, name: str) -> bytes:
    return data.replace(b'\r\n', b'\n') if name.endswith(TEXT) else data


def check_archives() -> int:
    for lesson in CONFIG['lessons']:
        stage, root = lesson['number'], lesson['root']
        with ZipFile(ROOT / 'downloads' / (root + '.zip')) as archive:
            assert archive.testzip() is None, root
            names = [name for name in archive.namelist() if not name.endswith('/')]
            assert not any(name.endswith('answer.md') for name in names), (root, 'В архиве ответ модели')
            for name in names:
                local = ROOT / 'exercises' / name
                assert local.is_file(), (root, 'Нет в exercises', name)
                assert normalized(local.read_bytes(), name) == normalized(archive.read(name), name), (root, 'Отличается', name)
            for track in CONFIG['tracks']:
                folder = root + '/' + track['folder'] + '/'
                skill = folder + '.opencode/skills/' + track['skill'] + '/'
                for required in ['source.md', 'facts.md', 'CHECKLIST.md', 'PROMPT.md', 'TASK.md', 'results/observations.md']:
                    assert folder + required in names, (root, required)
                assert (skill + 'SKILL.md' in names) == (stage >= 2), (root, track['folder'], 'SKILL.md')
                assert any(name.startswith(skill + 'references/') for name in names) == (stage >= 4), (root, 'references')
                for script in ['scripts/check.js', 'scripts/check.py']:
                    assert (skill + script in names) == (stage >= 5), (root, script)
                if stage >= 2:
                    text = archive.read(skill + 'SKILL.md').decode('utf-8')
                    header = text.split('---', 2)[1]
                    assert re.search(r'^name: ' + re.escape(track['skill']) + r'$', header, re.M), (root, 'name')
                    placeholder = any(word in text for word in ['Замените', 'Допишите', 'Добавьте'])
                    assert placeholder == (stage < 6), (root, track['folder'], 'Заготовка урока')
    for track in CONFIG['tracks']:
        folder = ROOT / 'skills' / track['skill']
        expected = {track['skill'] + '/' + p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
        with ZipFile(ROOT / 'downloads' / (track['skill'] + '.zip')) as archive:
            assert set(archive.namelist()) == set(expected), (track['skill'], 'Состав ZIP')
            for name, data in expected.items():
                assert normalized(archive.read(name), name) == normalized(data, name), (track['skill'], name)
        header = (folder / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
        assert 'Не применять' in header, (track['skill'], 'В описании нет границы применения')
    return len(CONFIG['lessons'])


def check_scripts() -> int:
    node = shutil.which('node')
    checks = 0
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        for track in CONFIG['tracks']:
            scripts = ROOT / 'skills' / track['skill'] / 'scripts'
            flagged_text, missed_text = SAMPLES[track['folder']]
            clean, missed, flagged = folder / 'clean.md', folder / 'missed.md', folder / 'flagged.md'
            clean.write_text('Обычная фраза без находок.\n', encoding='utf-8')
            missed.write_text(missed_text, encoding='utf-8')
            flagged.write_text(flagged_text, encoding='utf-8')
            before = flagged.read_bytes()
            commands = [[sys.executable, str(scripts / 'check.py')]]
            if node:
                commands.append([node, str(scripts / 'check.js')])
            outputs = []
            for command in commands:
                for arguments, code in [([clean], 0), ([missed], 0), ([flagged], 1), ([], 2), ([folder / 'none.md'], 2)]:
                    result = subprocess.run(command + [str(a) for a in arguments], capture_output=True, encoding='utf-8')
                    assert result.returncode == code, (command[-1], arguments, result.returncode, result.stderr)
                    checks += 1
                outputs.append(subprocess.run(command + [str(flagged)], capture_output=True, encoding='utf-8').stdout)
            assert flagged.read_bytes() == before, (track['skill'], 'Скрипт изменил файл')
            assert len(set(outputs)) == 1, (track['skill'], 'check.js и check.py находят разное')
    if not node:
        print('Node.js не найден: check.js не проверялся.')
    return checks


def main():
    pages, links = check_markdown()
    lessons = check_archives()
    runs = check_scripts()
    print(f'Проверено: {pages} страниц Markdown, {links} локальных ссылок, {lessons} архивов уроков по '
          f'{len(CONFIG["tracks"])} маршрута, {len(CONFIG["tracks"])} готовых скилла, {runs} запусков скриптов проверки.')


if __name__ == '__main__':
    main()
