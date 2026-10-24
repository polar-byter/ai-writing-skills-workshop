# Писательские навыки ИИ

Курс о том, как собрать свой скилл для агента: папку с правилами, образцами и проверкой, которую агент загружает сам, когда видит подходящую задачу. Вместо того чтобы в каждом диалоге заново объяснять модели одно и то же, вы один раз записываете правило и проверяете, что оно работает на настоящем ответе.

Учиться можно по одному из трёх маршрутов. Механика уроков общая, отличаются тексты и правила:

| Маршрут | С каким текстом работаем | Какой скилл соберёте |
|---|---|---|
| Рассказ | Черновик сцены из цикла о смотрителе маяка и канон цикла | `story-voice` |
| ТЗ | Заметки после звонка с сетью пекарен и подтверждённые факты | `clear-spec` |
| Перевод | Страница правил настольной игры, бриф издателя и глоссарий | `rulebook-translation` |

**[Начать с введения](course/00-introduction.md)** / **[Все уроки и материалы](course/README.md)** / **[Готовые промпты](course/prompts.md)**

## Путь по курсу

| Урок | Что получится | Архив |
|---|---|---|
| [0. Ставим OpenCode и выбираем маршрут](course/lesson-00-setup.md) | Модель отвечает в папке вашего маршрута | [writing-00-setup](downloads/writing-00-setup.zip?raw=true) |
| [1. Что модель делает без скилла](course/lesson-01-baseline.md) | Первый ответ и список конкретных промахов | [writing-01-baseline](downloads/writing-01-baseline.zip?raw=true) |
| [2. Первое правило в скилле](course/lesson-02-first-skill.md) | `SKILL.md`, загрузку которого видно в истории агента | [writing-02-first-skill](downloads/writing-02-first-skill.zip?raw=true) |
| [3. Правило, которое можно проверить](course/lesson-03-checkable-rule.md) | Два ответа, которые отличаются одним правилом | [writing-03-reader-context](downloads/writing-03-reader-context.zip?raw=true) |
| [4. Справка, которую агент читает сам](course/lesson-04-references.md) | Образцы в `references`, которые агент читает в нужный момент | [writing-04-references](downloads/writing-04-references.zip?raw=true) |
| [5. Что ловит скрипт и что ловите вы](course/lesson-05-checks.md) | Проверка слов в браузере, необязательно на Python силами агента | [writing-05-checks](downloads/writing-05-checks.zip?raw=true) |
| [6. Новый текст, чужой текст и другой проект](course/lesson-06-transfer.md) | Переносимая папка скилла с границами применения | [writing-06-transfer](downloads/writing-06-transfer.zip?raw=true) |
| [Заключение](course/conclusion.md) | План скилла для вашей собственной задачи | - |

## Как здесь учиться

Уроки можно читать прямо на GitHub. Для практики скачайте архив урока по ссылке в таблице или в самом уроке, распакуйте его и откройте в OpenCode папку своего маршрута: `story`, `spec` или `translation`. Каждый архив самостоятелен: в нём готовы все прошлые шаги, а текущий обозначен заготовкой. Содержимое архивов можно посмотреть и в браузере, в папке [exercises](exercises/README.md).

Готовые скиллы, с которыми удобно сверить свою версию после шестого урока: [story-voice](skills/story-voice/SKILL.md), [clear-spec](skills/clear-spec/SKILL.md), [rulebook-translation](skills/rulebook-translation/SKILL.md). Их же можно скачать архивами: [story-voice.zip](downloads/story-voice.zip?raw=true), [clear-spec.zip](downloads/clear-spec.zip?raw=true), [rulebook-translation.zip](downloads/rulebook-translation.zip?raw=true).

## Что понадобится

Компьютер с Windows, OpenCode Desktop и Блокнот. Программировать не нужно, платная подписка тоже: в каталоге OpenCode на 21.10.2026 были бесплатные модели, а в нулевом уроке мы первым делом проверяем, что модель отвечает. Python понадобится только в необязательном разделе пятого урока.

## Лицензия

Код распространяется по лицензии [MIT](LICENSE), тексты уроков и картинки - по [CC BY-NC-SA 4.0](LICENSE-CONTENT.md): их можно использовать и переделывать с указанием автора, не в коммерческих целях и под той же лицензией.

<details>
<summary>Для сопровождения курса</summary>

[Правила редактирования](AGENTS.md) / [Сборка и выгрузка](maintainer/README.md) / [Журнал работы](maintainer/WORK_LOG.md)

</details>
