# Gets image from Docker hub
FROM python:3.10-slim

WORKDIR /code

# Install system dependencies for OpenCV (libGL)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY ../pyproject.toml ../poetry.lock /code/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

COPY . /code/

# Port number of backend
EXPOSE 8000 
# Expose UDP port
EXPOSE 1234/udp

CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
