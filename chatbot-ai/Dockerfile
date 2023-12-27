FROM python:3.10-buster

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz \
    && rm dockerize-linux-amd64-v0.6.1.tar.gz

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD ["python", "main.py"]