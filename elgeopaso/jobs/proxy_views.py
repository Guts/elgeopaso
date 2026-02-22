import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proxy_jobs_api(request):
    """Proxy to fetch jobs data from external API."""
    try:
        response = requests.get(
            'https://elgeopaso.georezo.net/api/offres/?format=json&offset=25400',
            timeout=10
        )
        response.raise_for_status()  # Check for HTTP errors
        
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': str(e),
            'jobs': []  # Return empty array on error
        }, status=500)