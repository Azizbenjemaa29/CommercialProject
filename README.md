# CommercialProject (Django)

A Django web project serving the Halden Expeditions website.

---

## Quick Start: How to Run the Server

### 1. Open Terminal in the project directory
Make sure you are in `CommercialProject`.

### 2. Activate the Virtual Environment
- **PowerShell (Windows)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Command Prompt (cmd)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```

### 3. Start the Django Development Server
```powershell
python manage.py runserver
```
*(Or without activating the venv: `.\venv\Scripts\python manage.py runserver`)*

### 4. Open in your browser
Navigate to:
```
http://127.0.0.1:8000/
```

---

## Project Structure

```
CommercialProject/
│
├── config/                 # Project configuration (settings, root urls, wsgi/asgi)
│   ├── settings.py         # Django settings (apps, templates, allowed hosts)
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
│
├── pages/                  # Django app handling page views
│   ├── views.py            # Home view rendering index.html
│   ├── urls.py             # App-level URL routes
│   └── models.py           # Database models (expandable)
│
├── templates/              # HTML templates
│   └── index.html          # Main landing page template
│
├── venv/                   # Python virtual environment (Django installed)
├── db.sqlite3              # SQLite database
├── manage.py               # Django management CLI
├── requirements.txt        # Python package dependencies
└── .gitignore              # Git ignore rules for Python/Django
```

---

## Helpful Commands

- **Create an admin superuser**:
  ```powershell
  python manage.py createsuperuser
  ```
- **Apply migrations**:
  ```powershell
  python manage.py migrate
  ```
- **Access Admin Panel**:
  ```
  http://127.0.0.1:8000/admin/
  ```
