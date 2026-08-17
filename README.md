# MFS-Tool

The MSF Tool is a web-based application designed to digitize and automate the multi-source feedback evaluation process for physicians in rotating clinical residency programs.

The system generates individual invitation links asynchronously, evaluates incoming feedback via dynamic questionnaires, and adaptively generates follow-up questions when performance falls below defined thresholds.

## Main Features

- **Automated Invitations:** Scheduled email delivery (via Celery/Redis) for the 3- and 6-month evaluations
- **Secure Evaluation Without Logging In:** One-time links for evaluators
- **Adaptive Questionnaires (SurveyJS):** Dynamic generation of follow-up questions in the front end, based on historical database values (threshold < 60%)
- **Central Management:** Django admin dashboard for maintaining data (trainees, evaluators)
- **Visual Reporting:** Aggregation of raw data and graphical presentation of the results (means, standard deviations) for the review

## Technology Stack

- Backend: Django
- Frontend: SurveyJS, Chart.js
- Asynchronous Tasks: Celery, Redis
- Database: SQLite
- Deployment: Docker, Nginx, Gunicorn

## Installation

This project is fully containerized. You only need [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your server or local machine.

### 1. Clone the repository
```
git clone https://github.com/iccas-leipzig/MSF-Tool.git
cd MSF-Tool/MSF_Tool
```

### 2. Configure Environment Variables
Create a .env file in the root directory. You can copy the provided example file:
```
cp .env.example .env
```
Open the .env file and configure it to suit your needs.

### 3. Build and Start the Containers
Start the entire stack (Django, Gunicorn, Nginx, Celery, and Redis) in the background:
```
docker-compose up -d --build
```

### 4. Create an Admin User
Create a superuser account to access the administration dashboard:
```
docker-compose exec web python manage.py createsuperuser
```

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

## Licenses

* **[Django](https://www.djangoproject.com/)** - BSD License
* **[Redis](https://redis.io/)** - AGPLv3 License
* **[Celery](https://docs.celeryq.dev/)** - BSD License
* **[SurveyJS](https://surveyjs.io/)** - MIT License
