# Made in Izmir - Django Project

A Django-based web application for connecting Izmir's premium producers with global buyers through trade fairs and export services.

## Project Structure

```
made-in-izmir/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── main/                  # Main application
│   ├── static/           # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/        # HTML templates
│   ├── views.py          # View functions
│   ├── urls.py           # App URL patterns
│   └── models.py         # Database models
├── assets/               # Original assets (legacy)
├── manage.py             # Django management script
└── db.sqlite3           # SQLite database
```

## Static Files Organization

The project uses Django's static files system:

- **Development**: Static files are served from `main/static/`
- **Production**: Run `python manage.py collectstatic` to gather all static files into `staticfiles/`

### Static Files Structure:
```
main/static/
├── css/
│   └── style.css
├── js/
│   └── translations.js
└── images/
    └── (your images here)
```

## Setup Instructions

1. **Install Dependencies** (if needed):
   ```bash
   pip install django
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Available Pages

- `/` - Home page
- `/about/` - About page
- `/producers/` - For Producers
- `/buyers/` - For Buyers
- `/calendar/` - Trade Fair Calendar
- `/contact/` - Contact page

## Static Files in Templates

All templates use Django's `{% static %}` template tag:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/translations.js' %}"></script>
```

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in `config/settings.py`
2. Configure `ALLOWED_HOSTS` with your domain
3. Set a secure `SECRET_KEY`
4. Run `python manage.py collectstatic` to collect all static files
5. Use a production-ready web server (e.g., Gunicorn, uWSGI)
6. Serve static files with Nginx or a CDN

## Development Notes

- The project uses SQLite for development
- All HTML templates are in `main/templates/`
- Static files are organized in `main/static/`
- The original `assets/` folder is kept for reference but not used by Django

## License

© 2024 Made in İzmir. All Rights Reserved.
