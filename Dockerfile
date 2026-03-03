FROM python:3.13.12-slim
WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
EXPOSE 8000

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:app"]
