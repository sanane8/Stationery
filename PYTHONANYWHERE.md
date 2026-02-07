# Deploying on PythonAnywhere

## Fixes applied for 502 errors

- **`django.contrib.humanize`** added to `production_settings.py` (templates use it; missing = crash).
- **LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL** added so auth redirects work.
- **MEDIA_URL, MEDIA_ROOT** added (main `urls.py` uses them).
- **ALLOWED_HOSTS** includes `.pythonanywhere.com` so your subdomain is allowed.
- **WSGI** adds project root to `sys.path` so imports work.
- **DATABASES/STATIC_ROOT** use `str()` paths for compatibility.

## Checklist on PythonAnywhere

1. **Web tab**
   - **Source code**: set to your project folder (e.g. `/home/YOUR_USERNAME/Stationery`).
   - **WSGI configuration file**: point to your WSGI file, e.g.  
     `/home/YOUR_USERNAME/Stationery/stationery_tracker/wsgi.py`

2. **Virtualenv**
   - Create a virtualenv in the project (or a path you prefer).
   - In the Web app, set **Virtualenv** to that path (e.g. `/home/YOUR_USERNAME/Stationery/.venv` or `/home/YOUR_USERNAME/.virtualenvs/Stationery`).
   - In that virtualenv, install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Static files**
   - In project directory:
     ```bash
     python manage.py collectstatic --noinput --settings=stationery_tracker.production_settings
     ```
   - In **Web → Static files**:
     - URL: `/static/`
     - Directory: `/home/YOUR_USERNAME/Stationery/staticfiles`

4. **Database**
   - Run migrations:
     ```bash
     python manage.py migrate --settings=stationery_tracker.production_settings
     ```
   - Create a superuser if needed:
     ```bash
     python manage.py createsuperuser --settings=stationery_tracker.production_settings
     ```

5. **Reload**
   - Click **Reload** for your Web app (green button).

6. **If you still get 502**
   - Open **Web → Error log** and **Web → Server log** and check the last lines for the real Python traceback (e.g. `ModuleNotFoundError`, `InvalidTemplateLibrary`, or `ImproperlyConfigured`). Fix the reported error and reload again.

## Domain

If your site is `https://YOUR_USERNAME.pythonanywhere.com`, it’s already allowed via `.pythonanywhere.com`. For a custom domain, add it to `ALLOWED_HOSTS` in `stationery_tracker/production_settings.py`.
