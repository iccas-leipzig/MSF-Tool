from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SurveyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveyapp'

    verbose_name = _("Umfrage-Verwaltung")
