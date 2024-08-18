FROM python:3.10.11

WORKDIR /app

COPY req.txt .

RUN pip install --no-cache-dir -r req.txt

COPY . .

ENV FLASK_APP=app.py

CMD ["python", "app.py"]
