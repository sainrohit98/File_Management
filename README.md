# Project Setup

### 1. Create a project folder name file_manager

### 2. Clone from git repo
> git clone https://github.com/sainrohit98/File_Management.git

> python -m venv venv

> venv\bin\activate

> cd file_manager

### 3. Rename .env.example to .env and change secret values

### 4. Install requirements

> pip install -r requirements.txt

### 5. Run migrations

> python manage.py makemigrations

> python manage.py migrate

### 6. Run the project

> python manage.py runserver


# Celery Setup

### 1. Open new terminal

### 2. Activate the enviroment
> venv\bin\activate

### 3. Run below command
> celery -A file_manager worker -P gevent -l info


# Test Cases

### 1. Open new terminal

### 2. Activate the enviroment
> venv\bin\activate

### 3. Run below command
> python manage.py test file_app.tests















