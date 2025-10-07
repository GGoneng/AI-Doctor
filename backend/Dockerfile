FROM python:3.10

WORKDIR '/back'
RUN pip install python-multipart fastapi uvicorn[standard] --no-cache-dir
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]