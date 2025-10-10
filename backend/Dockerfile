FROM python:3.10

WORKDIR '/back'

RUN apt-get update && apt-get install -y libgl1

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]