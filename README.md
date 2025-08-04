# API генерации резюме (PDF)

Пример сервиса средней сложности, который принимает данные кандидата (имя, опыт и навыки) и возвращает сгенерированное PDF‑резюме. API построено на FastAPI, шаблон оформляется через Jinja2, конвертация в PDF выполняется библиотекой [`pdfkit`](https://pypi.org/project/pdfkit/) с использованием системного бинарника `wkhtmltopdf`.

## Возможности

* **POST `/generate-pdf`** — принимает JSON с полями `name`, `experience`, `skills`, опциональными `position` и `education`, а также опциональным `template`. Возвращает файл PDF. 
* Использование HTML+CSS шаблонов: в каталоге `templates` лежит базовый шаблон `resume_default.html` и более современный `resume_modern.html`, стилизованный по образцу резюме на hh.ru. Можно создавать собственные шаблоны и выбирать их, передавая имя в поле `template`.
* Возможность локализации: шаблоны могут быть подготовлены на разных языках; достаточно добавить соответствующие HTML‑файлы и указать их название в запросе.

## Структура проекта

```
resume_pdf_api/
├── main.py               # основной код FastAPI‑приложения
├── requirements.txt      # зависимости Python
├── Dockerfile            # рецепт сборки контейнера (включает wkhtmltopdf)
├── templates/
│   └── resume_default.html  # базовый шаблон резюме на русском
└── README.md             # текущий файл
```

## Требования

* Python 3.11+
* Библиотеки из `requirements.txt` (`pip install -r requirements.txt`)
* **wkhtmltopdf** — внешний бинарник для pdfkit. Его нужно установить самостоятельно (например, `sudo apt install wkhtmltopdf` на Debian/Ubuntu). На Windows нужно скачивать инсталлер(https://wkhtmltopdf.org/downloads.html) и прописывать путь до exe в переменную Path. В Docker‑образе установка происходит автоматически.

## Пример запроса

```bash
curl -X POST http://localhost:8000/generate-pdf \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Иван Иванов",
           "experience": [
             "Разработчик Python в XYZ, 2019–2021",
             "Инженер по данным в ABC, 2021–2023"
           ],
           "skills": ["Python", "FastAPI", "PostgreSQL"],
           "position": "Data Engineer",
           "education": [
             "Курс Apache Spark, 2023",
             "Университет XYZ, бакалавр информатики, 2018"
           ],
           "template": "resume_modern"
         }' --output resume.pdf
```

После выполнения запроса файл `resume.pdf` появится в текущем каталоге. В браузере можно обратиться к интерактивной документации Swagger по адресу `http://localhost:8000/docs`.

## Запуск локально

1. Создайте виртуальное окружение и активируйте его.
2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Убедитесь, что `wkhtmltopdf` доступен в системе (`wkhtmltopdf --version`). Если команда не найдена, установите пакет.

4. Запустите приложение:

   ```bash
   uvicorn main:app --reload
   ```

## Запуск в Docker

Docker‑файл уже содержит установку `wkhtmltopdf`. Сборка и запуск выглядят так:

```bash
docker build -t resume-api:latest .
docker run --rm -p 8000:8000 resume-api:latest
```

Теперь API будет доступно на `http://localhost:8000/generate-pdf`.

## Возможные расширения

* **Выбор шаблона:** добавить несколько HTML‑файлов с различными стилями оформления и передавать имя шаблона в поле `template`.
* **Перевод:** подготовить шаблоны на других языках (например, английском) и выбирать язык через параметр.
* **Хранение резюме:** сохранять сгенерированные PDF‑файлы на диск или в облако, предоставляя ссылку для скачивания позже.