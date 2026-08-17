from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from trainees.models import Trainee
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class SurveyResult(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_("Abgeschlossen von"), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    trainee = models.ForeignKey(Trainee, verbose_name=_("Auszubildende:r"), on_delete=models.CASCADE)

    data = models.JSONField()
    submitted_at = models.DateTimeField(verbose_name=_("Abgegeben am"), auto_now_add=True)

    MILESTONE_CHOICES = [
        (3, '3 Monate'),
        (6, '6 Monate'),
    ]
    milestone = models.IntegerField(verbose_name=_("Monat"), choices=MILESTONE_CHOICES, default=3)

    class Meta:
        verbose_name = _("Umfrage-Ergebnis")
        verbose_name_plural = _("Umfrage-Ergebnisse")

class SurveyInvitation(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    reviewer = GenericForeignKey('content_type', 'object_id')

    trainee = models.ForeignKey(Trainee, verbose_name=_("Auszubildende:r"), on_delete=models.CASCADE)

    sent_at = models.DateTimeField(verbose_name=_("Gesendet am"), default=timezone.now)
    reminded_at = models.DateTimeField(verbose_name=_("Erinnert am"), null=True, blank=True)
    completed_at = models.DateTimeField(verbose_name=_("Abgegeben am"), null=True, blank=True)

    MILESTONE_CHOICES = [
        (3, '3 Monate'),
        (6, '6 Monate'),
    ]
    milestone = models.IntegerField(verbose_name=_("Monat:"), choices=MILESTONE_CHOICES, default=3)

    class Meta:
        verbose_name = _("Umfrage-Einladung")
        verbose_name_plural = _("Umfrage-Einladungen")

    def __str__(self):
        return f"Invite: {self.reviewer} -> {self.trainee}"