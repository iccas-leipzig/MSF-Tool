from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry
from .models import SurveyResult, SurveyInvitation

from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule
)

celery_models = [
    PeriodicTask, 
    IntervalSchedule, 
    CrontabSchedule, 
    SolarSchedule, 
    ClockedSchedule
]

QUESTION_MAP = {
    "item1": "Stellt korrekte Diagnosen",
    "item2": "Entwickelt angemessene Behandlungspläne",
    "item3": "Ist sich eigener Grenzen bewusst / bittet um Hilfe",
    "item4": "Ordnet Maßnahmen im Bewusstsein der Kosten an",
    "item5": "Gutes Zeitmanagement / setzt Prioritäten",
    "item6": "Gute manuelle/technische Fähigkeiten",
    "item7": "Führt Krankengeschichte/Berichte zeitgerecht",
    "item8": "Kommuniziert adäquat mit Patienten/Angehörigen",
    "item9": "Bezieht psychosoziale Aspekte mit ein",
    "item10": "Behält Patientensicherheit im Blick",
    "item11": "Kommuniziert adäquat mit Kollegen",
    "item12": "Ist erreichbar und zuverlässig",
    "item13": "Gibt Wissen an junge Kollegen weiter",
    "item14": "Ist offen für Feedback und setzt es um",
    "item15": "Ist initiativ und übernimmt Verantwortung",
    "item16": "Gesamteindruck",
    
    "strenghts": "Besondere Stärken",
    "improvement": "Verbesserungsbereiche",
    "externalInfluences": "Äußere Einflüsse vorhanden?",
    "externalInfluencesComments": "Erläuterung Äußere Einflüsse",
    "workConditionsChange": "Vorschläge zur Veränderung?",
    "workConditionsChangeComments": "Vorschläge",
    "doubtsIntegrityHealth": "Zweifel an Integrität/Gesundheit?",
    "doubtsIntegrityHealthComments": "Bedenken",
}

# Hides periodic tasks on the admin dashboard
for model in celery_models:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Show results on the admin dashboard
@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ['get_trainee_name', 'get_respondent_name', 'get_respondent_type', 'submitted_at']
    readonly_fields = ['get_respondent_name', 'visualized_data']
    exclude = ['data', 'object_id']

    def get_trainee_name(self, obj):
        return f"{obj.trainee.first_name} {obj.trainee.last_name}"
    get_trainee_name.short_description = "Auszubildede:r"

    def get_respondent_name(self, obj):
        # obj.content_object fetches the specific Doctor or Nurse
        if obj.content_object:
            return f"{obj.content_object.first_name} {obj.content_object.last_name}"
        return "Gelöschtes Belegschaftsmitglied"
    get_respondent_name.short_description = "Bewerter:in"

    def get_respondent_type(self, obj):
        # This tells you if it is a Doctor or Nurse
        if obj.content_object:
            return obj.content_object._meta.verbose_name
        return "Unknown"
    get_respondent_type.short_description = "Beruf Bewerter:in"

    def visualized_data(self, obj):
        if not obj.data:
            return "Keine Daten"

        html_output = "<div style='max-width: 800px;'>"
        
        html_output += "<h3 style='background:#f0f0f0; color: black; padding:10px; border-bottom:2px solid #ccc;'>Bewertung (Skala 1-5)</h3>"
        html_output += "<table style='width:100%; border-collapse: collapse;'>"
        
        for i in range(1, 17):
            key = f"item{i}"
            value = obj.data.get(key)
            
            if value:
                width = (int(value) / 5) * 100
                
                color = "#4caf50"
                if int(value) < 3: color = "#f44336"
                elif int(value) == 3: color = "#ff9800"

                bar_html = f"""
                    <div style='background-color: #e0e0e0; border-radius: 4px; overflow: hidden; width: 150px; height: 20px;'>
                        <div style='background-color: {color}; width: {width}%; height: 100%; text-align:center; color:white; font-size:12px; line-height:20px;'>
                            {value}/5
                        </div>
                    </div>
                """
                
                html_output += f"""
                    <tr style='border-bottom: 1px solid #eee;'>
                        <td style='padding: 8px;'><b>{QUESTION_MAP.get(key, key)}</b></td>
                        <td style='padding: 8px;'>{bar_html}</td>
                    </tr>
                """

        html_output += "</table>"

        html_output += "<h3 style='background:#f0f0f0; color: black; padding:10px; border-bottom:2px solid #ccc; margin-top:20px;'>Kommentare & Details</h3>"
        
        text_fields = [
            "strenghts", "improvement", 
            "externalInfluences", "externalInfluencesComments",
            "workConditionsChange", "workConditionsChangeComments",
            "doubtsIntegrityHealth", "doubtsIntegrityHealthComments"
        ]

        for key in text_fields:
            value = obj.data.get(key)
            if value:
                label = QUESTION_MAP.get(key, key)
                html_output += f"""
                    <div style='margin-bottom: 15px; border-left: 4px solid #2196F3; padding-left: 10px;'>
                        <div style='font-weight: bold; color: #555;'>{label}</div>
                        <div style='font-size: 14px; margin-top: 4px;'>{value}</div>
                    </div>
                """

        html_output += "</div>"
        
        return format_html(html_output)

    visualized_data.short_description = "Umfrage Ergebnis"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Show invitations on the admin dashboard
@admin.register(SurveyInvitation)
class SurveyInvitationAdmin(admin.ModelAdmin):
    # Columns to show in the list
    list_display = [
        'get_reviewer', 
        'trainee', 
        'get_status_badge', 
        'sent_at', 
        'reminded_at', 
        'completed_at'
    ]
    
    # Filters on the right sidebar
    list_filter = [
        'sent_at', 
        'completed_at', 
        ('reminded_at', admin.EmptyFieldListFilter) # Filter by "Reminded" vs "Not Reminded"
    ]
    
    # Search box (Search by Trainee name)
    search_fields = ['trainee__last_name', 'trainee__first_name']

    readonly_fields = ['reviewer_link']
    fields = ['reviewer_link', 'trainee', 'sent_at', 'reminded_at', 'completed_at']

    def get_reviewer(self, obj):
        if obj.reviewer:
            return f"{obj.reviewer} ({obj.reviewer._meta.verbose_name})"
        return "Unbekannte:r Bewerter:in"
    get_reviewer.short_description = "Bewerter:in"

    def reviewer_link(self, obj):
        return self.get_reviewer(obj)
    reviewer_link.short_description = "Bewerter:in"

    def get_status_badge(self, obj):
        if obj.completed_at:
            color = 'green'
            text = 'Abgegeben'
        elif obj.reminded_at:
            color = 'orange'
            text = 'Erinnert'
        else:
            color = '#999' # Grey
            text = 'Ausstehend'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 12px;">{}</span>',
            color, text
        )
    get_status_badge.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# Show logs on the admin dashboard
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # What columns to display in the list view
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    
    # Add filters to the right sidebar
    list_filter = ['action_flag', 'action_time', 'user']
    
    # Make it read-only so admins can't tamper with the logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False