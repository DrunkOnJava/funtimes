FROM python:3.8-slim

WORKDIR /app
COPY . /app

# Install dependencies for tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./openai_cli3.py"]