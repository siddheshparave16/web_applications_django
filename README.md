# Task Management System

You can buy the book here: https://amzn.to/3u7MXVy

## Description
This Task Management System is a fully functional Django web application, developed as part of the hands-on learning experience offered by our book "Building Web Applications with Django". This system allows users to create, manage, and track tasks in a simple and intuitive interface.

## Key Features
- User registration and login functionality.
- Ability to create, update, and delete tasks.
- Task status tracking (Todo, In Progress, Done).
- Interactive and user-friendly dashboard to visualize tasks.
- Restful API

## Prerequisites
- Python 3.11
- Django 4.2
- poetry

## Getting Started
Clone the repository and navigate to the project directory:

```sh
git clone https://github.com/llazzaro/web_applications_django.git
cd web_applications_django
```

## Installation
Use pip to install the required dependencies:

```sh
poetry install
```


# Usage
Detailed usage instructions are found in the book, including step-by-step guides on how to interact with the system and implement each feature.

# Contributing
Please refer to the CONTRIBUTING.md for information on how to contribute to this project.

# License
This project is licensed under the MIT License. See the LICENSE.md file for details.

Task Manager (Django + PostgreSQL + Redis)
A Django web application for task management with Dockerized services.

🚀 Setup Guide
Prerequisites
Python 3.8+

Docker Desktop

Poetry (recommended) or pip

🛠 Installation
1. Clone the Repository
bash
git clone https://github.com/your-repo/task_manager.git
cd task_manager
2. Set Up Environment
With Poetry (recommended):
bash
poetry install  # Installs all dependencies
poetry shell    # Activates virtual environment
With traditional venv:
bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
3. Configure Database
bash
docker-compose up -d  # Starts PostgreSQL, Redis, and Mailhog
4. Apply Migrations
bash
python manage.py migrate
5. Create Superuser (Optional)
bash
python manage.py createsuperuser
🏃 Running the Application
bash
python manage.py runserver
Access: http://localhost:8000

🌐 Services
Service	Port	URL
Django	8000	http://localhost:8000
PostgreSQL	5432	db (in Docker)
Redis	6379	redis (in Docker)
Mailhog	8025	http://localhost:8025
🔧 Troubleshooting
Common Issues
Docker errors:

bash
docker-compose down -v  # Stops and removes containers
docker-compose up -d    # Rebuilds fresh containers
Missing dependencies:

bash
poetry install --no-root
Static files not loading:

Ensure DEBUG=True in .env

Run:

bash
python manage.py collectstatic
📂 Project Structure
task_manager/
├── taskmanager/          # Django project
├── docker-compose.yml    # Service configurations
├── pyproject.toml        # Poetry dependencies
└── .env.example          # Environment template
💻 Development
Always activate virtual environment first:

bash
poetry shell
Before committing:

bash
python manage.py makemigrations
python manage.py migrate
📝 License
MIT


ninja api

🗡️ Django Ninja API Endpoints
Quick Start
Ensure Django Ninja is installed:

bash
poetry add django-ninja
Access the automatic docs at:
http://localhost:8000/api/docs
