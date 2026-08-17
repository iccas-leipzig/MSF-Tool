from django.db import models
from django.utils import timezone
import uuid
from django.utils.translation import gettext_lazy as _

class Trainee(models.Model):
    first_name = models.CharField(verbose_name=_("Vorname"), max_length=100)
    last_name = models.CharField(verbose_name=_("Nachname"), max_length=100)
    email = models.EmailField(blank=False, null=True)
    created_at = models.DateTimeField(verbose_name=_("Beginn Ausbildungsphase:"), default=timezone.now)
    survey_round_1_sent = models.BooleanField(verbose_name=_("Bewertung nach drei Monaten gesendet"), default=False)
    survey_round_2_sent = models.BooleanField(verbose_name=_("Bewertung nach sechs Monaten gesendet"), default=False)

    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

        verbose_name = _("Auszubildende:r")
        verbose_name_plural = _("Auszubildende")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"