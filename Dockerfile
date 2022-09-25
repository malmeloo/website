FROM python:3-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver", "0:8000"]
