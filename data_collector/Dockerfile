FROM python:3.13-alpine

RUN apk add --no-cache postgresql-dev

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
