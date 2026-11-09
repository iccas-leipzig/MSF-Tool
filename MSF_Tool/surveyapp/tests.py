import json
import re
from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from staff.models import Doctor, Nurse, Therapist
from trainees.models import Trainee

from .models import SurveyInvitation
from .tasks import send_quarterly_surveys, send_six_month_surveys, send_survey_reminders


# Skips the 10 second delay between mails
@mock.patch("surveyapp.tasks.time.sleep")
class SurveyLinkTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(first_name="Dora", last_name="Doc", email="doc@example.com")
        self.nurse = Nurse.objects.create(first_name="Nina", last_name="Nurse", email="nurse@example.com")
        self.therapist = Therapist.objects.create(first_name="Theo", last_name="Ther", email="ther@example.com")
        self.trainee = Trainee.objects.create(
            first_name="Tina",
            last_name="Trainee",
            created_at=timezone.now() - timedelta(days=200),
        )

    # Returns the survey path contained in a mail body
    def survey_path(self, message):
        match = re.search(re.escape(settings.SITE_URL) + r"(/survey/\S+)", message.body)
        self.assertIsNotNone(match, message.body)
        return match.group(1)

    def assert_link_opens_survey(self, path, milestone):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "survey.html")
        self.assertEqual(response.context["milestone"], milestone)

    def test_three_month_links_are_valid(self, _sleep):
        send_quarterly_surveys()

        self.assertEqual(len(mail.outbox), 3)
        for message in mail.outbox:
            self.assert_link_opens_survey(self.survey_path(message), 3)

    def test_six_month_links_are_valid(self, _sleep):
        self.trainee.survey_round_1_sent = True
        self.trainee.save()

        send_six_month_surveys()

        self.assertEqual(len(mail.outbox), 3)
        self.assertFalse(SurveyInvitation.objects.exclude(milestone=6).exists())
        for message in mail.outbox:
            self.assert_link_opens_survey(self.survey_path(message), 6)

    def test_reminder_link_keeps_milestone(self, _sleep):
        invitation = SurveyInvitation.objects.create(
            reviewer=self.doctor,
            trainee=self.trainee,
            milestone=6,
            sent_at=timezone.now() - timedelta(days=4),
        )

        send_survey_reminders()

        self.assertEqual(len(mail.outbox), 1)
        self.assert_link_opens_survey(self.survey_path(mail.outbox[0]), 6)
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.reminded_at)

    def test_reminder_skips_deleted_reviewer(self, _sleep):
        sent_at = timezone.now() - timedelta(days=4)
        SurveyInvitation.objects.create(reviewer=self.doctor, trainee=self.trainee, milestone=3, sent_at=sent_at)
        SurveyInvitation.objects.create(reviewer=self.nurse, trainee=self.trainee, milestone=3, sent_at=sent_at)
        self.doctor.delete()

        send_survey_reminders()

        self.assertEqual([m.to for m in mail.outbox], [["nurse@example.com"]])

    def test_save_survey_completes_matching_milestone(self, _sleep):
        three_months = SurveyInvitation.objects.create(reviewer=self.doctor, trainee=self.trainee, milestone=3)
        six_months = SurveyInvitation.objects.create(reviewer=self.doctor, trainee=self.trainee, milestone=6)

        response = self.client.post(
            "/save-survey/",
            data=json.dumps({
                "survey_data": {"item1": "4"},
                "reviewer_id": str(self.doctor.public_id),
                "trainee_id": str(self.trainee.public_id),
                "milestone": 3,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        three_months.refresh_from_db()
        six_months.refresh_from_db()
        self.assertIsNotNone(three_months.completed_at)
        self.assertIsNone(six_months.completed_at)

    def test_invalid_link_is_logged(self, _sleep):
        path = f"/survey/{self.doctor.public_id}/{self.trainee.public_id}/6/"

        with self.assertLogs("surveyapp", level="WARNING") as logs:
            response = self.client.get(path)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error.html")
        self.assertIn("no invitation", logs.output[0])
