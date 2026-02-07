# Get your web app LIVE on PythonAnywhere

If the Error log shows "last loaded" at an old time and the site shows 502, the app is **crashing on startup** and never stays running. Follow these steps in order.

---

## Step 1: Put the latest code on PythonAnywhere

- **If you use Git:** In a **Bash console** on PythonAnywhere:
  ```bash
  cd ~/Stationery   # or your project path
  git pull
  ```
- **If you upload files:** Re-upload these so they match your local project:
  - `stationery_tracker/production_settings.py`
  - `stationery_tracker/wsgi.py`
  - (optional) `stationery_tracker/wsgi_pythonanywhere.py` for better error logging

---

## Step 2: Web tab – point to your project

1. Open **Web**.
2. **Code** section:
   - **Source code:** `/home/spmsabila/Stationery` (use your real path if different).
   - **Working directory:** leave empty or same as source code.
3. **WSGI configuration file:**
   - Click the link to edit the WSGI file.
   - It must point to your project’s WSGI module. Use **one** of these:

   **Option A (recommended for debugging):**  
   Path: `/home/spmsabila/Stationery/stationery_tracker/wsgi_pythonanywhere.py`  
   That file writes startup errors to `~/Stationery/error_wsgi.log` if Django fails to load.

   **Option B (standard):**  
   Path: `/home/spmsabila/Stationery/stationery_tracker/wsgi.py`

   The file **content** must look like this (and load your project):

   ```python
   import os
   import sys

   path = '/home/spmsabila/Stationery'   # ← your project path
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'stationery_tracker.production_settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

   Replace `/home/spmsabila/Stationery` with your actual project path.

4. **Virtualenv:** Set to your virtualenv, e.g. `/home/spmsabila/.venv` or `/home/spmsabila/Stationery/.venv`.

5. Save the WSGI file.

---

## Step 3: Virtualenv and dependencies

In a **Bash console**:

```bash
cd ~/Stationery
source ~/.venv/bin/activate   # or: source .venv/bin/activate
pip install -r requirements.txt
```

Fix any `pip` errors before continuing.

---

## Step 4: Database and static files

In the **same** Bash console (with virtualenv active):

```bash
cd ~/Stationery

python manage.py migrate --settings=stationery_tracker.production_settings

python manage.py collectstatic --noinput --settings=stationery_tracker.production_settings
```

If you don’t have a superuser yet:

```bash
python manage.py createsuperuser --settings=stationery_tracker.production_settings
```

---

## Step 5: Static files mapping (Web tab)

In **Web** → **Static files**:

| URL      | Directory                          |
|----------|------------------------------------|
| /static/ | /home/spmsabila/Stationery/staticfiles |

Use your real username and project path if different.

---

## Step 6: Reload the web app

1. In **Web**, click the green **Reload** button for your site.
2. Wait 10–20 seconds.
3. Open your site URL (e.g. `https://spmsabila.pythonanywhere.com`) in a new tab.

---

## Step 7: If you still get 502

The app is still crashing on startup. You need the **exact** error.

1. **Error log (Web tab)**  
   Open **Error log**, scroll to the **bottom**, and copy the **full** traceback (from the first `Traceback` line to the last line of the error).

2. **Startup log (if you use wsgi_pythonanywhere.py)**  
   In a Bash console:
   ```bash
   cat ~/Stationery/error_wsgi.log
   ```
   Copy the latest block (after the most recent `--- date ---`).

3. **Test Django in console**  
   In a **Bash** console:
   ```bash
   cd ~/Stationery
   source ~/.venv/bin/activate
   python manage.py check --settings=stationery_tracker.production_settings
   ```
   If this prints an error, fix that first (e.g. missing app, bad setting). Then Reload again.

4. **Common causes**
   - Wrong **project path** or **virtualenv** in the Web tab.
   - **Old code** on the server (Step 1 not done).
   - **Missing package:** install it in the same virtualenv you set in the Web tab.
   - **Import error** in your code or settings – the traceback will show the file and line.

---

## Checklist summary

- [ ] Latest code on PythonAnywhere (git pull or re-upload).
- [ ] Web → Source code = project directory.
- [ ] Web → WSGI file path = your `wsgi.py` or `wsgi_pythonanywhere.py`.
- [ ] WSGI file adds project path to `sys.path` and sets `DJANGO_SETTINGS_MODULE`.
- [ ] Web → Virtualenv = your venv path.
- [ ] `pip install -r requirements.txt` in that venv.
- [ ] `migrate` and `collectstatic` run with `--settings=stationery_tracker.production_settings`.
- [ ] Static files URL `/static/` mapped to `.../staticfiles`.
- [ ] **Reload** clicked, then site opened in browser.
- [ ] If 502: Error log (and `error_wsgi.log`) checked for full traceback; `manage.py check` run in console.

Once the app starts successfully, the Error log will show a **new** timestamp when you reload or open the site. Until then, fix the error shown in the log and reload again.
