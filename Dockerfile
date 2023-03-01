FROM python:3.8-alpine

RUN \
  apk update && \
  apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

WORKDIR /transaction_logs

COPY . .
COPY .env.example .env

RUN pip install -r requirements.txt
RUN ./manage.py check

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]
