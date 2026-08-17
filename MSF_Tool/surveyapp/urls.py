from django.urls import path
from . import views

urlpatterns = [
    path("survey/<uuid:reviewer_token>/<uuid:trainee_token>/<int:milestone>/", views.survey_page, name="survey_page"),
    path("save-survey/", views.save_survey, name="save_survey"),
    path("report/<uuid:trainee_id>/<int:months>/", views.trainee_report, name="trainee_report"),
    path('about/', views.about_page, name='about'),
]