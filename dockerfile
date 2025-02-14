# i want to create a that with docker compose will init the fron end (npm run start) and the backend (python main.py)

FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
RUN pip install  -r requirements.txt

COPY . .

CMD ["python", "main.py"]

