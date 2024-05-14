Для захисту від додавання чутливої інформації у коміт.
Можна застосувати автоматичнє сканування на сікрети/паролі та ін. перед виконанням GIT COMMIT

# Перший варіант

Для цього потрібно перемістити файл "pre-commit.sh" у діректорію .git/hooks та переіменувати в "pre-commit"
перевіривши наявність прав на виконання.
```shell
curl -fsL https://raw.githubusercontent.com/AZelyony/githook/main/pre-commit.sh
```

# Другий варіант

```shell
python3 pre-commit.py
```

Чи можна виконати наступну команду:

```shell
curl -fsL https://raw.githubusercontent.com/AZelyony/githook/main/pre-commit.py | python3 -
```
Зауважте, що важливо наявність прав адміна, чи запуск від sudo.

# Що далі?

При виконанні команди "git commit -m 'Some text'" gitleaks перевірить файли, що додаються до репозіторію на вміст чутливої інформації і зупинить коміт, щоб не було витоку.


За замовченням перевірки включені відразу після додавання pre-commit у .git/hooks чи інсталювання у другому способі.

Щоб тимчасово відключити перевірки, потрібно виконати команду:

```shell
git config --local --bool hooks.gitleaks.enabled false
```

Щоб включити перевірки, потрібно виконати команду:
```shell
git config --local --bool hooks.gitleaks.enabled true
```

## Хибні спрацювання.

Якщо є хибні спрацювання, то можливо ігнорувати конкретні виводи, створивши файл .gitleaksignore в корені вашого репозиторію.
Приклад - https://github.com/gitleaks/gitleaks/blob/master/.gitleaksignore


## Видалення
Видалення файла ".git/hooks/pre-commit" зупинить виконання перевірок на виток секретів перед commit.

Також можна видалити файл /usr/local/bin/gitleaks для ОС Linux.
Для MacOS видалити штатною командою.
Для ОС Windows - c:\Program Files\gitleaks\
