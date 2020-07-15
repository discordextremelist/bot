FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -U -r requirements.txt
CMD ["python", "./bot.py"]