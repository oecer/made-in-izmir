# Template Components Documentation

## 📁 Template Structure

Your Django project now uses a **component-based template system** for easy maintenance and consistency.

```
main/templates/
├── base.html                    # Base template (extends by all pages)
├── components/                  # Reusable components
│   ├── navbar.html             # Navigation bar
│   └── footer.html             # Footer
├── index.html                  # Home page
├── about.html                  # About page
├── producers.html              # Producers page
├── buyers.html                 # Buyers page
├── calendar.html               # Calendar page
└── contact.html                # Contact page
```

## 🎯 How It Works

### Base Template (`base.html`)
The base template contains the common HTML structure that all pages share:
- `<head>` section with meta tags and CSS links
- Navigation bar (via `{% include 'components/navbar.html' %}`)
- Content block (where page-specific content goes)
- Footer (via `{% include 'components/footer.html' %}`)
- JavaScript files

### Components

#### 1. **Navbar Component** (`components/navbar.html`)
Contains the complete navigation bar with:
- Logo
- Navigation links (Home, Producers, Buyers, Calendar, About, Contact)
- Language switcher (TR/EN)
- Mobile menu toggle

#### 2. **Footer Component** (`components/footer.html`)
Contains the footer with:
- Logo
- Description
- Copyright notice

### Page Templates
Each page extends the base template and only defines its unique content:

```django
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
<!-- Your page-specific content here -->
{% endblock %}
```

## ✏️ How to Make Changes

### To Change the Navigation Bar:
**Edit only ONE file**: `main/templates/components/navbar.html`

The change will automatically apply to **all pages**!

Example - Adding a new menu item:
```html
<!-- In components/navbar.html -->
<ul class="nav-links">
    <li><a href="{% url 'main:index' %}">Ana Sayfa</a></li>
    <li><a href="{% url 'main:producers' %}">Üreticiler İçin</a></li>
    <!-- Add your new link here -->
    <li><a href="{% url 'main:new_page' %}">New Page</a></li>
    ...
</ul>
```

### To Change the Footer:
**Edit only ONE file**: `main/templates/components/footer.html`

Example - Updating copyright year:
```html
<!-- In components/footer.html -->
<p>© 2026 Made in İzmir. Tüm Hakları Saklıdır.</p>
```

### To Change Common HTML Structure:
**Edit**: `main/templates/base.html`

Examples:
- Add a new CSS file
- Add Google Analytics
- Change meta tags
- Add new JavaScript libraries

```django
<!-- In base.html -->
<head>
    ...
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <!-- Add your new CSS here -->
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
</head>
```

### To Change Page Content:
**Edit the specific page template** (e.g., `index.html`, `about.html`)

You only need to edit the content inside `{% block content %}...{% endblock %}`

## 🎨 Template Blocks

### Available Blocks in `base.html`:

1. **`{% block title %}`** - Page title (appears in browser tab)
   ```django
   {% block title %}My Custom Title{% endblock %}
   ```

2. **`{% block extra_css %}`** - Add page-specific CSS
   ```django
   {% block extra_css %}
   <link rel="stylesheet" href="{% static 'css/page-specific.css' %}">
   {% endblock %}
   ```

3. **`{% block content %}`** - Main page content (required)
   ```django
   {% block content %}
   <h1>Your content here</h1>
   {% endblock %}
   ```

4. **`{% block extra_js %}`** - Add page-specific JavaScript
   ```django
   {% block extra_js %}
   <script src="{% static 'js/page-specific.js' %}"></script>
   {% endblock %}
   ```

## ✅ Benefits

1. **DRY (Don't Repeat Yourself)**: Navbar and footer defined once, used everywhere
2. **Easy Maintenance**: Change navbar/footer in one place, updates all pages
3. **Consistency**: All pages automatically have the same structure
4. **Flexibility**: Each page can still have unique content and styles
5. **Clean Code**: Page templates are much shorter and easier to read

## 📝 Example: Creating a New Page

1. **Create the template** (`main/templates/services.html`):
```django
{% extends 'base.html' %}

{% block title %}Made in Izmir - Services{% endblock %}

{% block content %}
<section class="section">
    <div class="container">
        <h1>Our Services</h1>
        <p>Service content here...</p>
    </div>
</section>
{% endblock %}
```

2. **Add the view** (in `main/views.py`):
```python
def services(request):
    return render(request, 'services.html')
```

3. **Add the URL** (in `main/urls.py`):
```python
path('services/', views.services, name='services'),
```

That's it! The new page automatically has the navbar and footer! 🎉

## 🔄 Before vs After

### Before (Repetitive):
- Each page had its own complete HTML structure
- Navbar code repeated 6 times
- Footer code repeated 6 times
- To change navbar, you had to edit 6 files

### After (Component-Based):
- Navbar defined once in `components/navbar.html`
- Footer defined once in `components/footer.html`
- To change navbar, edit only 1 file
- All pages automatically updated

## 🚀 This is a Django Best Practice!

You're now using the same template architecture that professional Django developers use in production applications.
