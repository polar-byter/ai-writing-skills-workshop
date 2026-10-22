"""Выгружаем читательский курс из Obsidian: страницы, анимации, архивы уроков, каркасы и готовые скиллы.

Файлы, изменённые в репозитории вручную, экспорт не перезаписывает: сначала перенесите правку в Obsidian.
"""
import argparse
import hashlib
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PLAIN = {'—': '-', '–': '-', '→': '->', '←': '<-', '…': '...', '\xa0': ' ', '\xab': '"',
         '\xbb': '"', '“': '"', '”': '"', '„': '"', '‘': "'", '’': "'", '−': '-'}
TEXT = ('.md', '.py', '.js', '.json', '.txt', '.html', '.csv', '.gitignore')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plain_punctuation(text: str) -> str:
    for old, new in PLAIN.items():
        text = text.replace(old, new)
    return text


def relative_link(source: Path, target: Path) -> str:
    return quote(os.path.relpath(target, source.parent).replace('\\', '/'), safe='/.-_')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', type=Path, required=True, help='Корень хранилища Obsidian')
    args = parser.parse_args()
    vault = args.vault.resolve()
    config = json.loads((ROOT / 'tools' / 'course-map.json').read_text(encoding='utf-8'))
    course = config['course']
    manifest_path = ROOT / 'maintainer' / 'export-manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'files': {}}

    # Ключ - путь от корня хранилища без .md, как его пишут в wiki-ссылках.
    mapping = {course + '/' + item['source'][:-3]: item['path'] for item in config['documents']}
    for lesson in config['lessons']:
        mapping[config['lesson_materials'] + '/' + lesson['root'] + '.zip'] = 'downloads/' + lesson['root'] + '.zip'
    for track in config['tracks']:
        mapping[config['skill_materials'] + '/' + track['skill'] + '.zip'] = 'downloads/' + track['skill'] + '.zip'
    pending = {}
    assets = {}

    def stage(relative: str, data: bytes) -> None:
        if relative.endswith(TEXT):
            data = data.replace(b'\r\n', b'\n')
        target = ROOT / relative
        if target.exists():
            current = target.read_bytes()
            known = previous['files'].get(relative)
            if current != data and (known is None or digest(current) != known):
                raise ValueError('Файл изменён вручную; экспорт его не перезаписал: ' + relative)
        pending[relative] = data

    def convert(text: str, destination: str) -> str:
        text = re.sub(r'\A---\n.*?\n---\n', '', text.replace('\r\n', '\n'), count=1, flags=re.S).lstrip()
        lines = [line for line in text.split('\n') if not any(marker in line for marker in config['drop_lines_with'])]
        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))

        def collapse(match):
            inner = re.sub(r'^> ?', '', match.group(2), flags=re.M).strip()
            return '<details>\n<summary>' + html.escape(match.group(1).strip()) + '</summary>\n\n' + inner + '\n\n</details>\n'
        text = re.sub(r'^> \[!\w+\]-\s*(.*?)\n((?:>.*(?:\n|$))+)', collapse, text, flags=re.M)

        def link(match):
            embedded, raw, label = match.groups()
            source = raw.rstrip('\\')  # в таблицах Obsidian разделитель подписи пишется как \|
            if embedded:
                target = 'assets/' + Path(source).name
                assets[source] = target
                width = int(label) if label and label.isdigit() else 480
                url = relative_link(Path(destination), Path(target))
                return f'<img src="{html.escape(url)}" width="{width}" alt="{html.escape(Path(source).stem)}">'
            if source not in mapping:
                raise ValueError('Нет читательского назначения для ссылки: ' + raw)
            url = relative_link(Path(destination), Path(mapping[source]))
            if url.endswith('.zip'):
                url += '?raw=true'
            return '[' + (label or Path(source).stem) + '](' + url + ')'
        text = re.sub(r'(!?)\[\[([^\]|]+)(?:\|([^\]]*))?\]\]', link, text)
        return plain_punctuation(text.strip()) + '\n'

    for document in config['documents']:
        destination = document['path']
        text = convert((vault / course / document['source']).read_text(encoding='utf-8'), destination)
        if 'lesson' in document:
            files = relative_link(Path(destination), Path('exercises') / document['lesson'] / 'README.md')
            heading, _, rest = text.partition('\n\n')
            text = heading + '\n\n[Файлы урока по трём маршрутам](' + files + ')\n\n' + rest
        stage(destination, text.encode('utf-8'))
    for source, destination in assets.items():
        stage(destination, (vault / source).read_bytes())

    pages = {item.get('lesson'): item['path'] for item in config['documents']}
    for lesson in config['lessons']:
        archive_path = vault / config['lesson_materials'] / (lesson['root'] + '.zip')
        stage('downloads/' + lesson['root'] + '.zip', archive_path.read_bytes())
        with ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            for name in archive.namelist():
                parts = Path(name).parts
                if not parts or parts[0] != lesson['root'] or '..' in parts:
                    raise ValueError('Недопустимый путь в архиве: ' + name)
                if name.endswith('/') or len(parts) == 1:
                    continue
                stage((Path('exercises') / Path(*parts)).as_posix(), archive.read(name))
        readme = Path('exercises') / lesson['root'] / 'README.md'
        rows = '\n'.join(f'| {track["label"]} | [{track["folder"]}]({track["folder"]}/TASK.md) | '
                         f'[{track["folder"]}/source.md]({track["folder"]}/source.md) |' for track in config['tracks'])
        text = (f'[Урок {lesson["number"]}. {lesson["title"]}]({relative_link(readme, Path(pages[lesson["root"]]))}) / '
                '[Все уроки](../../course/README.md)\n\n'
                f'# Файлы урока {lesson["number"]}\n\n'
                'Это распакованный архив урока, чтобы файлы можно было посмотреть в браузере. Для практики скачайте '
                f'[архив](../../downloads/{lesson["root"]}.zip?raw=true), распакуйте его и откройте в OpenCode папку своего маршрута.\n\n'
                '| Маршрут | Памятка | Исходный текст |\n|---|---|---|\n' + rows + '\n')
        stage(readme.as_posix(), text.encode('utf-8'))

    for track in config['tracks']:
        stage('downloads/' + track['skill'] + '.zip', (vault / config['skill_materials'] / (track['skill'] + '.zip')).read_bytes())
        folder = vault / config['skills_source'] / track['skill']
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                stage(('skills/' + track['skill'] + '/' + path.relative_to(folder).as_posix()), path.read_bytes())

    for relative, data in pending.items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {'format': 1, 'source': 'Obsidian: только читательский курс', 'documents': len(config['documents']),
                'lessons': len(config['lessons']), 'files': {key: digest(value) for key, value in sorted(pending.items())}}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Выгружено:', len(config['documents']), 'страниц,', len(config['lessons']), 'архивов уроков,',
          len(config['tracks']), 'готовых скилла,', len(assets), 'анимаций и картинок')


if __name__ == '__main__':
    main()
