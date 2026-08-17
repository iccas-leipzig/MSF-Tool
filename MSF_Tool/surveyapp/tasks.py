from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import get_connection, EmailMessage

import random
import textwrap
import time

from .models import SurveyInvitation
from trainees.models import Trainee
from staff.models import Doctor, Nurse, Therapist

# Sends mails for the 3-month survey
@shared_task
def send_quarterly_surveys():
    # Defines the threshold 76 days ago (14 days time for the survey)
    threshold_date = timezone.now() - timedelta(days=76)

    # Finds trainees older than threshold who haven't been processed
    trainees = Trainee.objects.filter(
        created_at__lte=threshold_date,
        survey_round_1_sent=False
    )

    if not trainees.exists():
        return "No 3-Month survey required today."

    all_doctors = list(Doctor.objects.all())
    all_nurses = list(Nurse.objects.all())
    all_therapists = list(Therapist.objects.all())

    emails_sent = 0
    emails_failed = 0

    for trainee in trainees:
        # Randomly selects 3 Doctors, 7 Nurses and 1 Therapist
        # min() handles cases where there's fewer staff than requested
        selected_doctors = random.sample(all_doctors, min(len(all_doctors), 3))
        selected_nurses = random.sample(all_nurses, min(len(all_nurses), 7))
        selected_therapists = random.sample(all_therapists, min(len(all_therapists), 1))
        
        reviewers = selected_doctors + selected_nurses + selected_therapists

        for reviewer in reviewers:
            invitation = SurveyInvitation.objects.create(
                reviewer=reviewer,
                trainee=trainee,
                milestone=3
            )

            url = f"{settings.SITE_URL}/survey/{reviewer.public_id}/{trainee.public_id}/3/"

            try:
                send_mail(
                    subject="Einladung zum Multi-Source-Feedback",
                    message=textwrap.dedent(f"""\
                                        Liebe:r {reviewer.first_name},
                                        
                                        du hattest dich zur Teilnahme am Multi-Source-Feedback für die ärztlichen Rotationsassistent:innen bereit erklärt. Vielen Dank an dieser Stelle bereits für dein Engagement um die ärztliche Weiterbildung zu unterstützen und zu verbessern!
                                        Heute ist es soweit: Wir bitten Dich um dein Feedback über {trainee.first_name} {trainee.last_name}.
                                        Folge bitte folgenden Link und beantworte die dort aufgelisteten Fragen!
                                        {url}
                                        Die Beantwortung der Fragen wird nicht länger als 5 Minuten Deiner Zeit in Anspruch nehmen.
                                        
                                        Vielen Dank für Deine Unterstützung und Deine Zeit, die Du dir dafür nimmst.
                                        Mit besten Grüßen
                                        
                                        Das Team der AG Lehre der
                                        Interdisziplinären Internistischen Intensivmedizin
                                        """),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reviewer.email],
                    fail_silently=False,
                )
                emails_sent += 1
                time.sleep(10)

            except Exception as e:
                emails_failed += 1
                print(f"Error sending 3-months survey to {reviewer.email}: {e}")

        trainee.survey_round_1_sent = True
        trainee.save()

    return f"3-Months: Processed {trainees.count()} trainees, sent {emails_sent} emails. {emails_failed} emails failed."

# Sends mails for the 6-month survey
@shared_task
def send_six_month_surveys():
    # Defines the threshold 166 days ago (14 days time for the survey)
    threshold_date = timezone.now().date() - timedelta(days=166)

    trainees = Trainee.objects.filter(
        created_at__lte=threshold_date,
        survey_round_1_sent=True,
        survey_round_2_sent=False
    )

    if not trainees.exists():
        return "No 6-Month survey required today."

    all_doctors = list(Doctor.objects.all())
    all_nurses = list(Nurse.objects.all())
    all_therapists = list(Therapist.objects.all())

    emails_sent = 0
    emails_failed = 0

    for trainee in trainees:
        # Randomly selects 3 Doctors, 7 Nurses and 1 Therapist
        # min() handles cases where there's fewer staff than requested
        selected_doctors = random.sample(all_doctors, min(len(all_doctors), 3))
        selected_nurses = random.sample(all_nurses, min(len(all_nurses), 7))
        selected_therapists = random.sample(all_therapists, min(len(all_therapists), 1))
    
        reviewers = selected_doctors + selected_nurses + selected_therapists

        for reviewer in reviewers:
            invitation = SurveyInvitation.objects.create(
                reviewer=reviewer,
                trainee=trainee,
                milestone=3
            )

            url = f"{settings.SITE_URL}/survey/{reviewer.public_id}/{trainee.public_id}/6/"

            try:
                send_mail(
                    subject="Einladung zum Multi-Source-Feedback",
                    message=textwrap.dedent(f"""\
                                        Liebe:r {reviewer.first_name},
                                        
                                        du hattest dich zur Teilnahme am Multi-Source-Feedback für die ärztlichen Rotationsassistent:innen bereit erklärt. Vielen Dank an dieser Stelle bereits für dein Engagement um die ärztliche Weiterbildung zu unterstützen und zu verbessern!
                                        Heute ist es soweit: Wir bitten Dich um dein Feedback über {trainee.first_name} {trainee.last_name}.
                                        Folge bitte folgenden Link und beantworte die dort aufgelisteten Fragen!
                                        {url}
                                        Die Beantwortung der Fragen wird nicht länger als 5 Minuten Deiner Zeit in Anspruch nehmen.
                                        
                                        Vielen Dank für Deine Unterstützung und Deine Zeit, die Du dir dafür nimmst.
                                        Mit besten Grüßen
                                        
                                        Das Team der AG Lehre der
                                        Interdisziplinären Internistischen Intensivmedizin
                                        """),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reviewer.email],
                    fail_silently=False,
                )
                emails_sent += 1
                time.sleep(10)

            except Exception as e:
                emails_failed += 1
                print(f"Error sending 6-months survey to {reviewer.email}: {e}")
        
        trainee.survey_round_2_sent = True
        trainee.save()

    return f"6-Months: Processed {trainees.count()} trainees, sent {emails_sent} emails. {emails_failed} emails failed."


# Sends reminder mails
@shared_task
def send_survey_reminders():
    # Defines reminder time
    reminder_threshold = timezone.now() - timedelta(days=3)

    # Finds pending invitations
    # - Sent more than 3 days ago (sent_at__lte)
    # - Not yet completed (completed_at__isnull=True)
    # - Not yet reminded (reminded_at__isnull=True)
    pending_invites = SurveyInvitation.objects.filter(
        sent_at__lte=reminder_threshold,
        completed_at__isnull=True,
        reminded_at__isnull=True
    )

    if not pending_invites.exists():
        return "No reminders needed today."

    emails_sent = 0
    emails_failed = 0

    for invite in pending_invites:
        reviewer = invite.reviewer
        trainee = invite.trainee
        milestone = invite.milestone
        
        url = f"{settings.SITE_URL}/survey/{reviewer.public_id}/{trainee.public_id}/{milestone}"

        try:
            send_mail(
                subject="Einladung zum Multi-Source-Feedback",
                message=textwrap.dedent(f"""\
                                    Liebe:r {reviewer.first_name},
                                    
                                    du hattest dich zur Teilnahme am Multi-Source-Feedback für die ärztlichen Rotationsassistent:innen bereit erklärt. Vielen Dank an dieser Stelle bereits für dein Engagement um die ärztliche Weiterbildung zu unterstützen und zu verbessern!
                                    Heute ist es soweit: Wir bitten Dich um dein Feedback über {trainee.first_name} {trainee.last_name}.
                                    Folge bitte folgenden Link und beantworte die dort aufgelisteten Fragen!
                                    {url}
                                    Die Beantwortung der Fragen wird nicht länger als 5 Minuten Deiner Zeit in Anspruch nehmen.
                                    
                                    Vielen Dank für Deine Unterstützung und Deine Zeit, die Du dir dafür nimmst.
                                    Mit besten Grüßen
                                    
                                    Das Team der AG Lehre der
                                    Interdisziplinären Internistischen Intensivmedizin
                                    """),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reviewer.email],
                fail_silently=False,
            )
            emails_sent += 1
            time.sleep(10)

        except Exception as e:
            emails_failed += 1
            print(f"Error sending reminder to {reviewer.email}: {e}")

        invite.reminded_at = timezone.now()
        invite.save()

    return f"Sent {emails_sent} reminder emails. {emails_failed} reminder emails failed."