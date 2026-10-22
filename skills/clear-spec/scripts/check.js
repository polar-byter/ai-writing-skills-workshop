// Подсказки для перечитывания: находит слова и обороты из списка PATTERNS.
// Одна и та же проверка работает на странице check.html и в Node.js.
// Файлы не изменяются; решение о каждой находке принимает человек.
const PATTERNS = [
  [
    "быстр|удобн|интуитивн|оптимальн|современн|надёжн|надежн|гибк",
    "размытое слово - чем это проверить?"
  ],
  [
    "user-friendly|простой и понятн|максимально|в кратчайшие сроки|как у всех",
    "размытое выражение"
  ],
  [
    "и т\\. ?д\\.|и т\\. ?п\\.|и др\\.|и прочее|и так далее",
    "список не закрыт - что именно входит?"
  ],
  [
    "при необходимости|по возможности|по мере надобности|если потребуется",
    "кто и когда решает, что это нужно?"
  ],
  [
    "должна поддерживать|должен поддерживать",
    "что именно должно происходить?"
  ]
];

function findHints(text) {
  const findings = [];
  const lines = text.split(/\r\n|\n|\r/);
  lines.forEach((line, index) => {
    for (const [source, hint] of PATTERNS) {
      const expression = new RegExp('(?<!\\p{L})(?:' + source + ')\\p{L}*', 'giu');
      for (const match of line.matchAll(expression)) {
        findings.push({line: index + 1, column: match.index + 1, fragment: match[0], hint});
      }
    }
  });
  return findings.sort((a, b) => a.line - b.line || a.column - b.column);
}

function formatFinding(finding) {
  return 'Строка ' + finding.line + ': "' + finding.fragment + '" - ' + finding.hint;
}

if (typeof document !== 'undefined') {
  const editor = document.getElementById('text');
  const status = document.getElementById('status');
  const results = document.getElementById('results');
  document.getElementById('file').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
      editor.value = await file.text();
      status.textContent = 'Файл открыт. Нажмите "Проверить".';
      results.replaceChildren();
    }
  });
  document.getElementById('check').addEventListener('click', () => {
    const findings = findHints(editor.value);
    results.replaceChildren();
    for (const finding of findings) {
      const item = document.createElement('li');
      item.textContent = formatFinding(finding);
      results.appendChild(item);
    }
    status.textContent = findings.length
      ? 'Мест, которые стоит перечитать: ' + findings.length + '.'
      : 'Скрипт ничего не нашёл. Теперь перечитайте текст по CHECKLIST.md.';
  });
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {findHints, formatFinding};
  if (require.main === module) {
    const fs = require('node:fs');
    const paths = process.argv.slice(2);
    if (!paths.length) {
      console.error('Укажите файл: node scripts/check.js results/answer.md');
      process.exitCode = 2;
    } else {
      try {
        let count = 0;
        for (const path of paths) {
          for (const finding of findHints(fs.readFileSync(path, 'utf8'))) {
            console.log(path + ': ' + formatFinding(finding));
            count += 1;
          }
        }
        console.log('Мест, которые стоит перечитать: ' + count + '. Смысл и факты скрипт не проверяет.');
        process.exitCode = count ? 1 : 0;
      } catch (error) {
        console.error('Не удалось прочитать файл: ' + error.message);
        process.exitCode = 2;
      }
    }
  }
}
