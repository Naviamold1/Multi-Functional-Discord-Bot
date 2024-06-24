FROM python:3-alpine

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --only main --no-root --no-directory

COPY . .

RUN poetry install --only main

CMD [ "python", "main.py" ]
