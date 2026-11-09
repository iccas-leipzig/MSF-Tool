# MSF-Tool

The MSF Tool is a web-based application designed to digitize and automate the multi-source feedback evaluation process for physicians in rotating clinical residency programs.

The system generates individual invitation links asynchronously, evaluates incoming feedback via dynamic questionnaires, and adaptively generates follow-up questions when performance falls below defined thresholds.

## Quick Start (Docker Image)

A ready-to-use image is published to the GitHub Container Registry. You only need [Docker](https://docs.docker.com/get-docker/) with the [Docker Compose](https://docs.docker.com/compose/install/) plugin; cloning the repository is not required.

### 1. Sign in to the registry and pull the image
> [!NOTE]
> The image is currently private, so you have to be signed in to the GitHub Container Registry with an account that has access to the [iccas-leipzig](https://github.com/iccas-leipzig) organization's packages. Pulling without signing in fails with `unauthorized`.

Create a [personal access token (classic)](https://github.com/settings/tokens/new?scopes=read:packages) with the `read:packages` scope and sign in with it (use your GitHub username):
```
echo <YOUR_TOKEN> | docker login ghcr.io -u <YOUR_GITHUB_USERNAME> --password-stdin
```
Docker stores the credentials, so this is only needed once per machine. Then pull the image:
```
docker pull ghcr.io/iccas-leipzig/multi_source_feedback:latest
```

### 2. Create a deployment directory with the configuration files
The example environment file and the Nginx configuration ship inside the image:
```
mkdir msf-tool && cd msf-tool
docker run --rm --entrypoint cat ghcr.io/iccas-leipzig/multi_source_feedback:latest /app/.env.example > .env
docker run --rm --entrypoint cat ghcr.io/iccas-leipzig/multi_source_feedback:latest /app/nginx/nginx.conf > nginx.conf
```
Open `.env` and fill in at least `SECRET_KEY`, `ALLOWED_HOSTS`, `SITE_URL`, `CSRF_TRUSTED_ORIGINS` and the `EMAIL_*` settings (`EMAIL_PORT` is required). A secure secret key can be generated with:
```
docker run --rm --entrypoint python ghcr.io/iccas-leipzig/multi_source_feedback:latest -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Create `docker-compose.yml`
```yaml
x-app: &app
  image: ghcr.io/iccas-leipzig/multi_source_feedback:latest
  env_file: .env
  restart: always
  depends_on:
    - redis

services:
  web:
    <<: *app
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/mediafiles
      - sqlite_data:/app/data

  worker:
    <<: *app
    # Skip the entrypoint: only the web container applies migrations
    entrypoint: []
    command: celery -A MSF_Tool worker --loglevel=info
    volumes:
      - sqlite_data:/app/data

  beat:
    <<: *app
    # Skip the entrypoint: only the web container applies migrations
    entrypoint: []
    command: celery -A MSF_Tool beat --loglevel=info
    volumes:
      - sqlite_data:/app/data

  nginx:
    image: nginx:1.25-alpine
    restart: always
    ports:
      - "80:80"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/mediafiles
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web

  redis:
    image: redis:7-alpine
    restart: always

volumes:
  static_volume:
  media_volume:
  sqlite_data:
```

### 4. Start the stack and create an admin user
```
docker compose up -d
docker compose exec web python manage.py createsuperuser
```
The application is now available at http://localhost (or your server's domain); see [Usage](#usage). Database migrations and static files are applied automatically on every start of the `web` container. The SQLite database lives in the `sqlite_data` volume.

### Updating and pinning versions
To update to the newest release, pull the new image and recreate the containers:
```
docker compose pull
docker compose up -d
```
Instead of `latest` you can pin a specific release in `docker-compose.yml` (e.g. `ghcr.io/iccas-leipzig/multi_source_feedback:0.1.1-alpha`). See [Releases and image tags](#releases-and-image-tags) for all available tags.

## Main Features

- **Automated Invitations:** Scheduled email delivery (via Celery/Redis) for the 3- and 6-month evaluations
- **Secure Evaluation Without Logging In:** One-time links for evaluators
- **Adaptive Questionnaires (SurveyJS):** Dynamic generation of follow-up questions in the front end, based on historical database values (mean role score < 3 on the five-point rating scale)
- **Central Management:** Django admin dashboard for maintaining data (trainees, evaluators)
- **Visual Reporting:** Aggregation of raw data and graphical presentation of the results (means, standard deviations) for the review

## Technology Stack

- Backend: Django
- Frontend: SurveyJS, Chart.js
- Asynchronous Tasks: Celery, Redis
- Database: SQLite
- Deployment: Docker, Nginx, Gunicorn

## Usage
Once the containers are running, the system is fully operational.

- **Access the Admin Dashboard:**
    Navigate to http://localhost/admin (or your server's domain). Log in with the superuser credentials you just created.
- **Add Personnel:**
    Add your clinical staff (Doctors, Nurses, Therapists) and the Trainees via the Admin panel.
- **Automated Invitations:**
    You do not need to send links manually. The Celery Beat worker runs in the background. Once a trainee hits the 3-month or 6-month milestone based on their created_at date, the system will automatically randomly select      reviewers and email them their unique, one-time-use survey links.
- **Evaluate:**
    Reviewers click the link in their email and fill out the SurveyJS-powered questionnaire in their browser. No login is required for reviewers.
- **View Results:**
    As soon as surveys are completed, administrators can view the aggregated feedback reports (calculated averages and standard deviations) via the web dashboard.

## Development

### Running from source with Docker Compose
Clone the repository and create an environment file (set `DEBUG=1` to see error pages):
```
git clone https://github.com/iccas-leipzig/MSF-Tool.git
cd MSF-Tool/MSF_Tool
cp .env.example .env
```
Build and start the whole stack (Django/Gunicorn, Nginx, Celery worker and beat, Redis) from your local code:
```
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```
The app is served through Nginx at http://localhost and directly by Gunicorn at http://localhost:8000. Rebuild with `--build` after changing the code.

### Running tests locally
The tests run without Docker. They need Python 3.11 and use Django's in-memory email backend, but `EMAIL_PORT` must still be set:
```
cd MSF_Tool
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export EMAIL_PORT=25
python manage.py makemigrations --check --dry-run   # fails if a model change has no migration
python manage.py test
```
After changing a model, create the migration with `python manage.py makemigrations` and commit it together with the change.

### Continuous integration
Every push to `main` or `dev`, every pull request and every version tag runs the [CI workflow](.github/workflows/ci.yml) on GitHub-hosted runners. It checks for missing migrations and runs the test suite. For pushes (not pull requests) it then builds the Docker image and publishes it to `ghcr.io/iccas-leipzig/multi_source_feedback`.

### Releases and image tags
| Event | Published image tags |
|---|---|
| Push to `main` | `latest` |
| Push to `dev` | `dev` |
| Version tag `v1.2.3` (or `1.2.3`) | `1.2.3` and `latest` |
| Pre-release tag `v1.2.3-alpha` (or `1.2.3-alpha`) | `1.2.3-alpha` only |

To publish a release, create a GitHub release from `main` with a new [semantic version](https://semver.org/) tag such as `v0.2.0`. The leading `v` is dropped from the image tag, and pre-releases (tags containing `-`) never update `latest`.

## Licenses

* **[Django](https://www.djangoproject.com/)** - BSD License
* **[Redis](https://redis.io/)** - AGPLv3 License
* **[Celery](https://docs.celeryq.dev/)** - BSD License
* **[SurveyJS](https://surveyjs.io/)** - MIT License
