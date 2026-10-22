"""Подсказки для перечитывания: находит слова и обороты из списка PATTERNS.

Тот же список, что в check.js, только для запуска через Python:
    python scripts/check.py results/answer.md
Файлы не изменяются; решение о каждой находке принимает человек.
"""
import re
import sys

PATTERNS = [
    ('грустн|печал|тоск|одинок|скучал по', 'чувство выражено словами - покажите его действием'),
    ('стыд|страх|страшн|боял|тревог|радост|счастлив|отчаяни', 'чувство выражено словами - покажите его действием'),
    ('сердце (?:сжалось|ёкнуло|екнуло|бешено|забилось|защемило)', 'затёртый оборот'),
    ('ком в горле|слёзы навернул|слезы навернул|предательск|волна (?:эмоций|чувств)', 'затёртый оборот'),
    ('время (?:остановилось|замерло)|словно вечность|казалось, вечность|пронзительн', 'затёртый оборот'),
    ('свинцов|яростно бил|завывал', 'пейзажный штамп'),
    ('телефон|смартфон|интернет|ноутбук|мобильн', 'проверьте: было ли это в 1974 году на маяке'),
]

# В Python нет \p{L}; [^\W\d_] означает "буква".
LETTER = r'[^\W\d_]'


def find_hints(text):
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for source, hint in PATTERNS:
            expression = re.compile(r'(?<!' + LETTER + r')(?:' + source.replace(r'\p{L}', LETTER) + r')' + LETTER + '*', re.IGNORECASE)
            for match in expression.finditer(line):
                findings.append((number, match.start() + 1, match.group(0), hint))
    return sorted(findings)


def main(paths):
    if not paths:
        print('Укажите файл: python scripts/check.py results/answer.md', file=sys.stderr)
        return 2
    count = 0
    try:
        for path in paths:
            with open(path, encoding='utf-8') as file:
                text = file.read()
            for number, _, fragment, hint in find_hints(text):
                print(f'{path}: Строка {number}: "{fragment}" - {hint}')
                count += 1
    except OSError as error:
        print('Не удалось прочитать файл: ' + str(error), file=sys.stderr)
        return 2
    print(f'Мест, которые стоит перечитать: {count}. Смысл и факты скрипт не проверяет.')
    return 1 if count else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
