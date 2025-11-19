# Dockerfile (place at repo root)
FROM python:3.12-slim

# set a working dir
WORKDIR /app

# system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# copy source
COPY . /app

# install python deps
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port used by uvicorn
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
