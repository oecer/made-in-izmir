# Quick Start Guide - Made in Izmir Django Project

## 🚀 Start the Server

```bash
python manage.py runserver
```

Then open your browser to: **http://127.0.0.1:8000/**

## 📄 Available Pages

**Important**: Django URLs do NOT use `.html` extensions. Use these URLs:

- **Home**: http://127.0.0.1:8000/
- **About**: http://127.0.0.1:8000/about/
- **Producers**: http://127.0.0.1:8000/producers/
- **Buyers**: http://127.0.0.1:8000/buyers/
- **Calendar**: http://127.0.0.1:8000/calendar/
- **Contact**: http://127.0.0.1:8000/contact/
- **Admin Panel**: http://127.0.0.1:8000/admin/

**Note**: All navigation links in the templates use Django's `{% url %}` tag, so clicking links will work correctly.

## 🛠️ Common Commands

### Create Admin User
```bash
python manage.py createsuperuser
```

### Run Migrations (after model changes)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files (for production)
```bash
python manage.py collectstatic
```

### Run Tests
```bash
python manage.py test
```

## 📁 Where to Add Content

### Add Images
Place images in: `main/static/images/`

Use in templates:
```html
{% load static %}
<img src="{% static 'images/your-image.jpg' %}" alt="Description">
```

### Add CSS
Edit: `main/static/css/style.css`

### Add JavaScript
Edit: `main/static/js/translations.js`

Or create new JS files in: `main/static/js/`

### Edit Templates
All HTML templates are in: `main/templates/`

## 🔧 Configuration

Main settings file: `config/settings.py`

- Change `DEBUG = False` for production
- Update `ALLOWED_HOSTS` with your domain
- Configure database settings if needed

## 📦 Install Dependencies

If setting up on a new machine:
```bash
pip install -r requirements.txt
```

## ✅ Project Status

✅ Django project initialized
✅ Static files organized
✅ All templates converted to Django format
✅ URL routing configured
✅ Database migrated
✅ Development server running

**Your Django project is ready to use!** 🎉
