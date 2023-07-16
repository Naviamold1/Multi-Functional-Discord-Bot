FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install pipenv && pipenv install --dev --system --deploy

COPY . .

CMD [ "python", "main.py" ]
