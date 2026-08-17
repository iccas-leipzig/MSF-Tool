from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TraineesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trainees'

    verbose_name = _("Auszubildende")