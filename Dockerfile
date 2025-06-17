
FROM python:3.11-slim

WORKDIR /app

COPY bot.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV BOT_TOKEN="BOT_TOKEN"

CMD ["python", "bot.py"]
