
# Library Management System (LMS)

## Installation Guide

Follow these steps to set up and run the project locally.

### Prerequisites

Make sure you have the following installed:

- **Docker Desktop**  
  Make sure Docker Desktop is installed.

- **Python 3.10 or higher**  
  Check your Python version:
  ```sh
  python --version
  ```

- **Node.js**  
  Check your Node.js version:
  ```sh
  npm -v
  ```

### Steps to Run the Backend with Docker

1. **Clone the entire repository:**
   ```sh
   git clone https://github.com/mansijp/LMS_CAPSTONE_2025.git
   ```

2. **Navigate to each microservice folder:**
   For each of the 7 microservices, follow these steps:

   ```sh
   cd <microservice-folder-names>
   ```

3. **Create a Docker image for each microservice:**
   Make sure you have Docker Desktop installed and run the following command in each microservice directory:
   ```sh
   docker build -t <microservicename1> .
   docker build -t <microservicename2> .
   docker build -t <microservicename3> .
   docker build -t <microservicename4> .
   docker build -t <microservicename5> .
   docker build -t <microservicename6> .
   docker build -t <microservicename7> .
   ```

4. **Run all the Docker images:**
   Open a _**new terminal**_ for each microservice and run the Docker containers on different ports:
   ```sh
   docker run -p 8001:8001 <microservicename1>
   docker run -p 8002:8002 <microservicename2>
   docker run -p 8003:8003 <microservicename3>
   docker run -p 8004:8004 <microservicename4>
   docker run -p 8005:8005 <microservicename5>
   docker run -p 8006:8006 <microservicename6>
   docker run -p 8008:8008 <microservicename7>
   ```

5. **Access the microservices:**
   After running the Docker containers, you can access the application through the first microservice
   ```sh
   http://127.0.0.1:8001/microservicename1
   ```

## Technologies Used

### Backend

- Python, FastAPI
- MongoDB

### Frontend

- JavaScript, Bootstrap, CSS, HTML

### DevOps

- Docker, Kubernetes
- Nginx Ingress, Google Cloud

## Architecture

- Microservices for independent features
- Nginx Ingress for inter-service and frontend-backend communication
- MongoDB for data storage (epubs, mp3s, images, text)
- SendInBlue (Brevo) for external email communication service
- Secure authentication using JWT tokens and session cookies

## Contributors
- Vaishali Jadon 
- Mansi Patel
- Astha Patel
- Atiya Azeez

**Note:** README file credits: Mansi Patel

## Original Repository:

**Note:** The original repository may not be available, so the current repository reflects the deployed web application.

>[LMS_CAPSTONE_2025](https://github.com/asthapatel1125/LMS_CAPSTONE_2025)
