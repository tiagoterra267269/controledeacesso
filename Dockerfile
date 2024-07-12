FROM python:3.12.3

WORKDIR /app

COPY Aplicacao/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY Aplicacao/ .

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]