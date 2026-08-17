from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *

# Show trainees on the admin dashboard
@admin.register(Trainee)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at', 'link_to_3_month_report', 'link_to_6_month_report')
    search_fields = ('first_name', 'last_name', 'email', 'created_at')
    readonly_fields = ('public_id', 'link_to_3_month_report', 'link_to_6_month_report', 'survey_round_1_sent', 'survey_round_2_sent')
    #readonly_fields = ('public_id', 'link_to_3_month_report', 'link_to_6_month_report')

    # Generates button to view the 3-months report
    def link_to_3_month_report(self, obj):
        url = reverse('trainee_report', args=[obj.public_id, 3])
        
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color:#4caf50; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Anzeigen</a>',
            url
        ) 
    link_to_3_month_report.short_description = "Bewertung nach 3 Monaten"

    # Generates button to view the 6-months report
    def link_to_6_month_report(self, obj):
        url = reverse('trainee_report', args=[obj.public_id, 6])
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color:#2196F3; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Anzeigen</a>',
            url
        ) 
    link_to_6_month_report.short_description = "Bewertung nach 6 Monaten"