FROM python:3.13-alpine

# Install PostgreSQL development dependencies se usiamo la slim o la completa non c'è bisogno
RUN apk add --no-cache postgresql-dev

# Copy application files
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your app
CMD ["python", "app.py"]
