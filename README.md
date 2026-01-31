# Made in Izmir Website

This is the static frontend for the Made in Izmir project.

## Structure
- `index.html`: Home page
- `producers.html`: Services and forms for producers
- `buyers.html`: Sourcing and industry info for buyers
- `calendar.html`: Expo calendar
- `about.html`: Company info
- `contact.html`: Contact forms
- `assets/`: CSS, JS, and eventual images

## Features
- **Bilingual Support**: Text is dynamically loaded via `assets/js/translations.js`. To add new translations, update the JSON object in that file.
- **Responsive Design**: Works on mobile and desktop.
- **Glassmorphism UI**: Modern aesthetic using CSS classes.

## How to Run
Simply open `index.html` in your web browser.

## Future Django Integration
To port this to Django later:
1. Move the HTML files to your Django `templates` directory.
2. Move the `assets` folder to your Django `static` directory.
3. Replace the `<link>` and `<script>` paths with static template tags (e.g., `{% static 'css/style.css' %}`).
4. Replace the hardcoded navigation links with Django URL tags (e.g., `{% url 'home' %}`).
