FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential libpq-dev curl

WORKDIR /app

COPY base/requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY base/ .

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base.settings

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
