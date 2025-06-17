
FROM python:3.11-slim

WORKDIR /app

COPY bot.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV BOT_TOKEN="7708285429:AAGkctX9eio3Ex76MPgVtVTvnJMMkvMSVRw"

CMD ["python", "bot.py"]
