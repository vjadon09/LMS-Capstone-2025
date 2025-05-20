# Dockerfile for User_Management

FROM python:3.10.0

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/app /app

EXPOSE 8006

CMD ["python", "main.py"]

# Build docker image
# docker build -t microservice_name:latest .

# See docker images
# docker images

# See running docker images
# docker ps

# Run the docker image
# docker run -p 8000:8000 customer_autentication:latest