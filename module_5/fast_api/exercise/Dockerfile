FROM python:3.11-alpine3.18

WORKDIR /usr/app

COPY requirements.txt /usr/app

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /usr/app

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]