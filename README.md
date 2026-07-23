# EnTree — Django Client Application

A Django-based client application for the EnTree job-matching platform, built as the front-end layer for **INFODBM Final Project (Group 2, BTIS3)**. This app is a thin client — all business logic (matching, filtering, login validation, auditing) lives inside SQL Server as stored procedures, views, functions, and triggers. Django's job here is only to call those objects and render the results.

## Tech Stack
- **Backend:** Django 6.x
- **Database:** Microsoft SQL Server (`EnTreeDB_Finals`)
- **DB Connector:** `mssql-django` + `pyodbc`
- **Frontend:** Django templates + Bootstrap 5 + Bootstrap Icons

## Prerequisites
Before setting up, make sure you have:
1. **Python 3.10+** installed and on PATH (`python --version` to check)
2. **SQL Server** running locally, with the `EnTreeDB_Finals` database restored/created
3. **ODBC Driver 17 (or 18) for SQL Server** installed — [download here](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
4. All required stored procedures, views, functions, and triggers already created in `EnTreeDB_Finals` (see `/sql` folder if included, or the project documentation)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/EnTree-Django-App.git
cd EnTree-Django-App
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# or
source .venv/bin/activate       # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the database connection

Open `entree_config/settings.py` and update the `DATABASES` block to match your SQL Server authentication method.

#### Option A: SQL Server Authentication (username + password)
Use this if you log into SSMS with a SQL login (e.g., `sa`) and a password.

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'EnTreeDB_Finals',
        'USER': 'sa',
        'PASSWORD': 'YOUR_PASSWORD_HERE',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

#### Option B: Windows Authentication (Trusted Connection)
Use this if you log into SSMS via "Windows Authentication" (no SQL username/password, just your Windows login). Leave `USER` and `PASSWORD` out entirely and add `Trusted_Connection`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'EnTreeDB_Finals',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    }
}
```

> **Note:** If your SQL Server uses a named instance (e.g., `localhost\SQLEXPRESS` instead of just `localhost`), update the `HOST` value accordingly for either option above.

> **Tip:** Not sure which one you're using? Open SSMS and check the login screen you use to connect — if there's a username/password field you fill in, use **Option A**; if it just says "Windows Authentication" with no fields to fill, use **Option B**.

### 5. Run Django's internal migrations
This creates Django's own framework tables (`django_session`, etc.) inside `EnTreeDB_Finals` — it will **not** touch or modify any existing EnTree tables.
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

## Test Login Credentials
Use any pre-seeded applicant from the database, for example:
| Email | Password |
|---|---|
| eisensy@email.com | eisensy123 |
| jed.engbino@email.com | jedlawrence123 |

## Project Structure
EnTreeProject/
├── entree_config/ # Django project settings, root URLs
├── core/
│ ├── models.py # Unmanaged models mirroring existing SQL tables
│ ├── db_utils.py # All stored procedure / view / function calls
│ ├── views.py # Request handling, session management
│ ├── urls.py # App-level routes
│ └── templates/core/ # HTML templates (Bootstrap-styled)
├── manage.py
└── requirements.txt