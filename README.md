# Django Project Setup

This is a Django project configured for development.

## Setup Instructions

### 1. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Create .env File
Copy `.env.example` to `.env` and update with your settings:
```powershell
copy .env.example .env
```

### 4. Run Migrations
```powershell
python manage.py migrate
```

### 5. Create Superuser (Optional)
```powershell
python manage.py createsuperuser
```

### 6. Start Development Server
```powershell
python manage.py runserver
```

The server will be available at `http://localhost:8000`

## Project Structure

- `config/` - Django configuration (settings, URLs, WSGI, ASGI)
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies

## Features

- Django REST Framework configured
- CORS headers enabled for frontend integration
- SQLite database (can be changed to PostgreSQL)
- Static files configuration
- Debug toolbar ready

## Next Steps

1. Create Django apps with: `python manage.py startapp app_name`
2. Define models in each app's `models.py`
3. Create serializers for REST API
4. Register URLs in `config/urls.py`
