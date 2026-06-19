FROM python:3.12-slim

WORKDIR /app

RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/temp

ENV DATABASE_URL=sqlite+aiosqlite:////app/data/bot.db

CMD ["python", "main.py"]
