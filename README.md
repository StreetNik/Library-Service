# Library-Service

## Project Overview
The Modern Library Management System is a comprehensive digital solution designed to transform and streamline library operations. This project aims to modernize library services, making them user-friendly, efficient, and accessible. Here's an overview of the key components:

The project leverages several technologies and features, including:

- **Django REST framework**: A robust toolkit for building Web APIs.
- **Simple JWT authorization**: Token-based authentication for secure API access.
- **Swagger documentation**: Interactive API documentation for easy testing and exploration.
- **Celery**: A distributed task queue system for background processing.
- **Celery Beat**: A scheduler for running periodic tasks.
- **Stripe**: The project leverages the Stripe payment platform to facilitate secure and seamless online transactions. Stripe allows users to make payments using various methods, including credit and debit cards. This integration enables the project to handle financial transactions, ensuring a smooth and reliable payment experience for users. 

## Installation

To run the project using Docker Compose, follow these steps:

1. Ensure you have Docker installed on your system.

2. Create a copy of the `.env.sample` file as `.env` and configure the environment variables as needed for your specific setup.

3. Build the Docker containers:

   ```bash
   docker-compose build
   docker-compose up -d
4. Access the development server and API at http://localhost:8000.

## Features

### Celery Tasks
The Library component includes a Celery task defined in tasks.py. This task automatically check and if payment link is not expired and if so change status of payment to expired so user can update link when he is ready to pay. Also, there is task which check is there any book which should be returned by tomorrow and if so send notification to telegram chat.  The task is scheduled using Celery Beat.

### Authentication and Authorization Token
Secure API access is ensured through Simple JWT token-based authentication. To interact with protected API endpoints, acquire an access token by registering or logging in as a user. Include the token in the Authorization header of your API requests.

### Telegram Notifications
Every time user made a successful payment or when its almost time to return the book, we receive notification about it in telegram chat.

For any questions or further assistance, feel free to reach out to:

E-mail: nikulicastas2004@gmail.com,
[GitHub Profile](https://github.com/StreetNik)