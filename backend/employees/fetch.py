import requests
from django.http import JsonResponse

from backend.employees.forms import ProfileForm



def fetch_countries_choices(request):
    form = ProfileForm()
    countries = form.fetch_countries_choices()
    return JsonResponse(countries, safe=False)


def fetch_states(request, country_code):
    url = f"https://country-api-1.onrender.com/states/states/{country_code}/"
    response = requests.get(url)
    if response.status_code == 200:
        states = response.json().get(country_code, [])
        return JsonResponse(states, safe=False)
    else:
        return JsonResponse([], safe=False)
