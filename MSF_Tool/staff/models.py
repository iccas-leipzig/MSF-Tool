from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

class Doctor(models.Model):
    first_name = models.CharField(verbose_name=_("Vorname"), max_length=100)
    last_name = models.CharField(verbose_name=_("Nachname"), max_length=100)
    email = models.EmailField(blank=False, null=True)
    created_at = models.DateTimeField(verbose_name=_("Erstellt am"), auto_now_add=True)

    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

        verbose_name = _("Arzt/Ärztin")
        verbose_name_plural = _("Ärzte/Ärztinnen")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Nurse(models.Model):
    first_name = models.CharField(verbose_name=_("Vorname"), max_length=100)
    last_name = models.CharField(verbose_name=_("Nachname"), max_length=100)
    email = models.EmailField(blank=False, null=True)
    created_at = models.DateTimeField(verbose_name=_("Erstellt am"), auto_now_add=True)

    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

        verbose_name = _("Pfleger/Pflegerin")
        verbose_name_plural = _("Pfleger/Pflegerinnen")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Therapist(models.Model):
    first_name = models.CharField(verbose_name=_("Vorname"), max_length=100)
    last_name = models.CharField(verbose_name=_("Nachname"), max_length=100)
    email = models.EmailField(blank=False, null=True)
    created_at = models.DateTimeField(verbose_name=_("Erstellt am"), auto_now_add=True)

    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

        verbose_name = _("Therapeut/Therapeutin")
        verbose_name_plural = _("Therapeuten/Therapeutinnen")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"