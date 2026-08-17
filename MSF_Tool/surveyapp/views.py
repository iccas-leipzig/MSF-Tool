import statistics

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from datetime import timedelta
from collections import defaultdict

import json
from .models import SurveyResult, SurveyInvitation
from staff.models import Doctor, Nurse, Therapist
from trainees.models import Trainee

QUESTION_MAP = {
    "item1": "Diagnosen",
    "item2": "Behandlungspläne",
    "item3": "Kennt Grenzen",
    "item4": "Kostenbewusstsein",
    "item5": "Zeitmanagement",
    "item6": "Manuelle Fähigkeiten",
    "item7": "Dokumentation",
    "item8": "Kommunikation Pat.",
    "item9": "Psychosoziales",
    "item10": "Patientensicherheit",
    "item11": "Teamkommunikation",
    "item12": "Zuverlässigkeit",
    "item13": "Lehrtätigkeit",
    "item14": "Feedbackkultur",
    "item15": "Initiative",
    "item16": "Gesamteindruck",
}

CATEGORY_MAP = {
    "medical_expert": ["item1", "item2", "item3", "item6"],
    "communicator": ["item7", "item8", "item9"],
    "member_of_team": ["item11", "item12"],
    "responsibility": ["item4", "item5", "item15"],
    "advisor": ["item10"],
    "scholar": ["item13", "item14"],
    "professional": ["item16"],
}

CATEGORY_TRANSLATION = {
    "medical_expert": "Medizinische:r Expert:in",
    "communicator": "Kommunikator:in",
    "member_of_team": "Mitglied eines Teams",
    "responsibility": "Verantwortungsträger:in",
    "advisor": "Gesundheitsberater:in und -fürsprecher:in",
    "scholar": "Gelehrte:r",
    "professional": "Professionell Handelnde:r",
    }

EXTRA_QUESTION_MAP = {
    "extra_med_diagnoses": "Medizinische:r Expert:in: Differenzialdiagnose",
    "extra_med_examination": "Medizinische:r Expert:in: Untersuchung und Befundinterpretation",
    "extra_med_therapy": "Medizinische:r Expert:in: Therapie",
    "extra_kom_1": "Kommunikator:in: Spricht klar und deutlich",
    "extra_kom_2": "Kommunikator:in: Spricht Patient:innen mit Namen an",
    "extra_kom_3": "Kommunikator:in: Stellt sich Patient:innen vor",
    "extra_kom_4": "Kommunikator:in: Wendet Zeit auf, um Details zu erfassen",
    "extra_kom_5": "Kommunikator:in: Hört aufmerksam zu",
    "extra_kom_6": "Kommunikator:in: Vermittelt ein angenehmes Gefühl",
    "extra_kom_7": "Kommunikator:in: Erklärt Behandlungsplan verständlich",
    "extra_kom_8": "Kommunikator:in: Antwortet in verständlicher Sprache",
    "extra_kom_9": "Kommunikator:in: Zeigt Mitgefühl bei schlechten Nachrichten",
    "extra_kom_10": "Kommunikator:in: Zeitnahe Kommunikation",
    "extra_kom_11": "Kommunikator:in: Effektives Zuhören und Zusammenfassen",
    "extra_kom_12": "Kommunikator:in: Hohe Qualität schriftlicher Kommunikation",
    "extra_team_management": "Mitglied eines Teams: Team Management",
    "extra_team_information": "Mitglied eines Teams: Informationsaustausch",
    "extra_team_3": "Mitglied eines Teams: Verhindert, löst oder schlichtet Konflikte in einem Team",
    "extra_resp_prio": "Verantwortungsträger:in: Priorisierung von Interventionen",
    "extra_resp_orga": "Verantwortungsträger:in: Organisation",
    "extra_resp_adjust": "Verantwortungsträger:in: Anpassungsfähigkeit",
    "extra_resp_help": "Verantwortungsträger:in: Hilfe anfordern",
    "extra_advisor_1": "Gesundheitsberater:in und -fürsprecher:in: Stellt Fragen zu den Lebensgewohnheiten der Patient:innen",
    "extra_advisor_2": "Gesundheitsberater:in und -fürsprecher:in: Erläutert Patient:innen die mit ihren persönlichen Entscheidungen verbundenen Risiken",
    "extra_advisor_3": "Gesundheitsberater:in und -fürsprecher:in: Bietet Patient:innen Programme zur Gesundheitsförderung an",
    "extra_advisor_4": "Gesundheitsberater:in und -fürsprecher:in: Überweist Patient:innen an andere den Bedürfnissen orientierten Unterstützungsangeboten",
    "extra_advisor_5": "Gesundheitsberater:in und -fürsprecher:in: Informiert Patient:innen über Vorsorgeprogramme",
    "extra_scholar_1": "Gelehrte:r: Engagiert sich durch kontinuierliches Lernen für die kontinuierliche Verbesserung der beruflichen Tätigkeit",
    "extra_scholar_2": "Gelehrte:r: Unterrichtet bzw. erläutert Inhalte gegenüber Studierenden und andere medizinischen Fachberufen",
    "extra_scholar_3": "Gelehrte:r: Integrieret aktuelle Evidenz in die Praxis",
    "extra_scholar_4": "Gelehrte:r: Trägt zur Schaffung und Verbreitung von gesundheitsbezogenen Wissen und dessen Anwendung bei",
    "extra_prof_1": "Professionell Handelnde:r: Kleidet sich professionell",
    "extra_prof_2": "Professionell Handelnde:r: Tritt sauber und gepflegt auf",
    "extra_prof_3": "Professionell Handelnde:r: Wirkt selbstbewusst",
    "extra_prof_4": "Professionell Handelnde:r: Präsentiert sich professionell auftretend",
    "extra_prof_5": "Professionell Handelnde:r: Zeigt verantwortungsbewusste Arbeitsgewohnheiten, Enthusiasmus und Motivation",
    "extra_prof_6": "Professionell Handelnde:r: Interagiert auf respektvolle und mitfühlende Weise mit Patient:innen",
    "extra_prof_7": "Professionell Handelnde:r: Zeigt Integrität, Ehrlichkeit, Mitgefühl und Respekt gegenüber anderen",
    "extra_prof_8": "Professionell Handelnde:r: Behandelt Patient:innen als Menschen und nicht als Fall",
    "extra_prof_9": "Professionell Handelnde:r: Urteilt nicht über den Lebensstil von Patient:innen",
    "extra_prof_10": "Professionell Handelnde:r: Urteilt nicht über Behandlungsentscheidungen von Patient:innen",
    "extra_prof_11": "Professionell Handelnde:r: Zeigt Bewusstsein für die eigenen Grenzen",
    }

# Returns staff member based on the token
def get_respondent_by_token(token):
    # Try finding a Doctor first
    try:
        return Doctor.objects.get(public_id=token)
    except Doctor.DoesNotExist:
        pass
    
    # If not found, try finding a Nurse
    try:
        return Nurse.objects.get(public_id=token)
    except Nurse.DoesNotExist:
        pass

    # If not found, try finding a Therapist
    try:
        return Therapist.objects.get(public_id=token)
    except Therapist.DoesNotExist:
        return None

# Renders the survey page
def survey_page(request, reviewer_token, trainee_token, milestone):
    # Find the Reviewer
    reviewer = get_respondent_by_token(reviewer_token)
    if not reviewer:
        raise Http404("Reviewer not found")

    # Find the Trainee
    trainee = get_object_or_404(Trainee, public_id=trainee_token)

    # Find the specific invitation for this link
    invitation = SurveyInvitation.objects.filter(
        object_id=reviewer.id,
        content_type__model=reviewer._meta.model_name,
        trainee=trainee,
        milestone=milestone
    ).last()

    if not invitation:
        return render(request, "error.html", {"message": "Ungültiger Link."})
        
    # Has it already been completed
    if invitation.completed_at is not None:
        return render(request, "already_completed.html", {
            "trainee": trainee
        })

    weak_categories = []
    
    # Check for adaptive questions (if 6-months survey and threshold is < 60%)
    if milestone == 6:
        past_results = SurveyResult.objects.filter(trainee=trainee, milestone=3)
        
        if past_results.exists():
            category_totals = {category: {"scored": 0, "max": 0} for category in CATEGORY_MAP.keys()}

            for result in past_results:
                data = result.data if isinstance(result.data, dict) else json.loads(result.data)
                
                for category, items in CATEGORY_MAP.items():
                    for item in items:
                        if item in data and str(data[item]).isdigit():
                            category_totals[category]["scored"] += int(data[item])
                            category_totals[category]["max"] += 5

            for category, scores in category_totals.items():
                if scores["max"] > 0:
                    percentage = scores["scored"] / scores["max"]
                    if percentage < 0.60:
                        weak_categories.append(category)


    context = {
        "reviewer_id": str(reviewer.public_id),
        "trainee_id": str(trainee.public_id),
        "milestone": milestone,
        "weak_categories": json.dumps(weak_categories),
        
        "trainee_name": f"{trainee.first_name} {trainee.last_name}"
    }
    return render(request, "survey.html", context)

# Saves the survey results
@csrf_exempt 
def save_survey(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        
        survey_data = payload.get('survey_data')
        reviewer_id = payload.get('reviewer_id')
        trainee_id = payload.get('trainee_id')
        milestone = payload.get('milestone')

        # Find who this is
        reviewer = get_respondent_by_token(reviewer_id)
        trainee = get_object_or_404(Trainee, public_id=trainee_id)

        if reviewer and trainee:
            SurveyResult.objects.create(
                content_object=reviewer,
                trainee=trainee,
                milestone=milestone,         
                data=survey_data
            )

            invitation = SurveyInvitation.objects.filter(
                object_id=reviewer.id,
                content_type__model=reviewer._meta.model_name,
                trainee=trainee,
                completed_at__isnull=True
            ).last()

            if invitation:
                invitation.completed_at = timezone.now()
                invitation.save()

            return JsonResponse({"status": "ok"})
            
    return JsonResponse({"status": "error"}, status=400)

# Renders the survey result for specific trainee and milestone
def trainee_report(request, trainee_id, months):
    trainee = get_object_or_404(Trainee, public_id=trainee_id)

    surveys = SurveyResult.objects.filter(
        trainee=trainee,
        milestone=months
    )

    if not surveys.exists():
        return render(request, "no_data.html", {"trainee": trainee, "months": months})

    scores = defaultdict(list)
    comments = defaultdict(list)

    extra_scores = defaultdict(list)

    text_fields = [
        "strenghts", 
        "improvement", 
        "externalInfluencesComments",
        "workConditionsChangeComments",
        "doubtsIntegrityHealthComments"
    ]

    # Gets all survey results for that trainee
    for survey in surveys:
        data = survey.data
        
        for i in range(1, 17):
            key = f"item{i}"
            if key in data and data[key]:
                try:
                    scores[key].append(int(data[key]))
                except ValueError:
                    pass
        
        for key in EXTRA_QUESTION_MAP.keys():
            if key in data and data[key]:
                try:
                    extra_scores[key].append(int(data[key]))
                except ValueError:
                    pass
        
        for key in text_fields:
            val = data.get(key)
            if val:
                comments[key].append(val)
        
        if data.get("externalInfluences") == "Ja" and not data.get("externalInfluencesComments"):
            comments["externalInfluencesComments"].append("Ja (Keine Erläuterung)")
            
        if data.get("workConditionsChange") == "Ja" and not data.get("workConditionsChangeComments"):
            comments["workConditionsChangeComments"].append("Ja (Keine Erläuterung)")
            
        if data.get("doubtsIntegrityHealth") == "Ja" and not data.get("doubtsIntegrityHealthComments"):
            comments["doubtsIntegrityHealthComments"].append("Ja (Keine Erläuterung)")

    chart_labels = []
    chart_data = []
    chart_sd = []

    # Calculates the average and standard deviation
    for key, values in scores.items():
        if values:
            avg_score = sum(values) / len(values)
            sd_score = statistics.stdev(values) if len(values) > 1 else 0.0

            chart_labels.append(QUESTION_MAP.get(key, key)) 
            chart_data.append(round(avg_score, 2))
            chart_sd.append(round(sd_score, 2))

    category_labels = []
    category_data = []
    category_sd = []
    category_table = []

    # Displays the results
    for category_name, items in CATEGORY_MAP.items():
        category_scores = []

        for item in items:
            if item in scores:
                category_scores.extend(scores[item])
        
        if category_scores:
            cat_avg = sum(category_scores) / len(category_scores)
            cat_sd = statistics.stdev(category_scores) if len(category_scores) > 1 else 0.0

            display_name = CATEGORY_TRANSLATION.get(category_name, category_name)

            category_labels.append(display_name)
            category_data.append(round(cat_avg, 2))
            category_sd.append(round(cat_sd, 2))

            category_table.append({
                "name": display_name,
                "avg": round(cat_avg, 2),
                "sd": round(cat_sd, 2)
            })
    
    # Displays the adaptive questions
    extra_table = []
    for key, values in extra_scores.items():
        if values:
            avg_score = sum(values) / len(values)
            sd_score = statistics.stdev(values) if len(values) > 1 else 0.0

            extra_table.append({
                "name": EXTRA_QUESTION_MAP.get(key, key),
                "avg": round(avg_score, 2),
                "sd": round(sd_score, 2),
                "count": len(values) # Shows how many doctors actually answered this specific extra question
            })

    context = {
        "trainee": trainee,
        "months": months,
        "survey_count": surveys.count(),
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "chart_sd": chart_sd,
        "category_labels": category_labels,
        "category_data": category_data,
        "category_sd": category_sd,
        "category_table": category_table,
        "extra_table": extra_table,
        "comments": dict(comments), # Convert defaultdict to normal dict
    }

    return render(request, "report.html", context)

# Renders the about page
def about_page(request):
    return render(request, "admin/about.html")