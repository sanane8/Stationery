# Deploy Stationery Tracker to Railway

This guide walks you through deploying the Django Stationery Management System to [Railway](https://railway.app).

---

## Prerequisites

- A [Railway](https://railway.app) account (GitHub login is easiest).
- Your project in a **Git** repository (GitHub, GitLab, or Bitbucket).
- Railway CLI (optional; you can do everything in the dashboard).

---

## Step 1: Push Your Code to Git

Ensure your project is committed and pushed to GitHub (or your chosen provider):

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin master
```

---

## Step 2: Create a New Project on Railway

1. Go to [railway.app](https://railway.app) and sign in.
2. Click **“New Project”**.
3. Choose **“Deploy from GitHub repo”** and select your Stationery repository.
4. Railway will detect the app and use the **Procfile** to run:  
   `gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT`

---

## Step 3: Add a PostgreSQL Database

1. In your Railway project, click **“+ New”**.
2. Select **“Database”** → **“PostgreSQL”**.
3. Wait for the database to be created. Railway will set **`DATABASE_URL`** automatically when you link the service (next step).

---

## Step 4: Link the Database to Your Web Service

1. Click your **web service** (the one created from GitHub).
2. Open the **“Variables”** tab.
3. Click **“Add a variable reference”** or **“Connect”** and attach the **PostgreSQL** service.  
   This adds `DATABASE_URL` to your app’s environment so Django uses PostgreSQL instead of SQLite.

---

## Step 5: Set Required Environment Variables

In the **Variables** tab of your web service, add (or confirm) these:

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Secret key for Django (generate a new one for production) | Long random string |
| `DJANGO_SETTINGS_MODULE` | Must be `stationery_tracker.production_settings` | `stationery_tracker.production_settings` |

Optional (for email, SMS, etc.):

| Variable | Description |
|----------|-------------|
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP for password reset / emails |
| `AFRICASTALKING_USERNAME`, `AFRICASTALKING_API_KEY`, `AFRICASTALKING_SENDER_ID` | Africa’s Talking SMS |

Generate a secret key (run locally once):

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Step 6: Configure Build and Start (if needed)

Railway usually detects:

- **Build:** `pip install -r requirements.txt`
- **Start:** from **Procfile**: `web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:${PORT:-8000}`

If you use a different requirements file, set in the service **Settings**:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** leave empty to use the Procfile, or set:  
  `gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT`

**Root directory:** If your app is not at the repo root, set **Root Directory** to the folder that contains `manage.py` (e.g. leave blank if `manage.py` is at root).

---

## Step 7: Run Migrations and Collect Static Files

Railway can run one-off commands. Use the **CLI** or add a **one-off run** in the dashboard.

**Option A – Railway CLI**

1. Install: `npm i -g @railway/cli` (or see [Railway CLI](https://docs.railway.app/develop/cli)).
2. Log in: `railway login`.
3. Link project: `railway link` (select your project and service).
4. Run:

```bash
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

**Option B – Deploy hook (recommended)**

Add a **release command** so migrations and static files run on every deploy:

1. In your **web service** → **Settings**.
2. Find **“Build”** or **“Deploy”** section.
3. Set **Release Command** to:

```bash
python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

Then deploy. After the first deploy, create a superuser via CLI:

```bash
railway run python manage.py createsuperuser
```

---

## Step 8: Generate a Domain

1. Open your **web service**.
2. Go to **Settings** → **Networking** (or **“Generate domain”**).
3. Click **“Generate domain”**. You’ll get a URL like `https://your-app.up.railway.app`.

`ALLOWED_HOSTS` is already configured in `production_settings.py` for `*.railway.app` and `*.up.railway.app`, so no code change is needed.

---

## Step 9: Verify the Deployment

1. Open the generated URL in a browser.
2. You should see the login page (or dashboard if already logged in).
3. Log in with the superuser you created.
4. Test: sales, products, static files (CSS), and any SMS/email if configured.

---

## Summary Checklist

- [ ] Code pushed to GitHub (or connected repo).
- [ ] New Railway project created from repo.
- [ ] PostgreSQL database added and linked (so `DATABASE_URL` is set).
- [ ] `DJANGO_SECRET_KEY` and `DJANGO_SETTINGS_MODULE` set in Variables.
- [ ] Release command set: `python manage.py migrate --noinput && python manage.py collectstatic --noinput`.
- [ ] Domain generated and app opens in browser.
- [ ] Superuser created via `railway run python manage.py createsuperuser`.
- [ ] Login and main features tested.

---

## Troubleshooting

- **App won’t start:** Check **Deploy logs** and **Variables**. Ensure `DATABASE_URL` is set and `DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings`.
- **502 / “Application failed”:** Ensure the start command uses `$PORT` (Procfile does). Check that Gunicorn is binding to `0.0.0.0:$PORT`.
- **Static files missing:** Run `collectstatic` (release command or `railway run python manage.py collectstatic --noinput`). The app uses WhiteNoise to serve static files.
- **Database errors:** Confirm PostgreSQL is linked and `DATABASE_URL` is present. For external DBs, you may need to allow SSL or set `DISABLE_DATABASE_SSL=1` only if your provider does not use SSL.

---

## Optional: Custom Domain

In **Settings** → **Networking**, add a **custom domain** and point your DNS (CNAME or A record) as Railway instructs. Then add that hostname to `ALLOWED_HOSTS` in `production_settings.py` (e.g. via an env var like `CUSTOM_DOMAIN`) or deploy a small update that includes it.

You’re done. Your Stationery app is now running on Railway with PostgreSQL.
