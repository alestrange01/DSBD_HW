FROM python:3.13-alpine

# Installa le dipendenze di sistema necessarie
RUN apk add --no-cache g++ gcc musl-dev libffi-dev postgresql-dev

# Copia i file dell'applicazione
WORKDIR /app
COPY . /app

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando per eseguire l'applicazione
CMD ["python", "app.py"]
