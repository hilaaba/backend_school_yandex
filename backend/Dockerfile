FROM python:3.7-slim

WORKDIR /app

COPY ../backend .

RUN python3 -m pip install --upgrade pip
# Install Apple M1 specific packages. Remove if you use another hardware
# RUN apt-get update && apt-get -y install libpq-dev gcc && pip3 install psycopg2
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "ya_disk.wsgi:application", "--bind", "0:8080"]