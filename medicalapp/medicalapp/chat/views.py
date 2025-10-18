import os
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')


@csrf_exempt
@require_POST
def proxy_message(request):
    """Receive a user message and proxy to Gemini-like API. Expects JSON {"message": "..."}.

    IMPORTANT: This view reads the GEMINI_API_KEY from environment. Do NOT commit keys into repo.
    """
    if GEMINI_API_KEY is None:
        return HttpResponseServerError(json.dumps({'error': 'Server misconfigured: GEMINI_API_KEY not set'}), content_type='application/json')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON'}), content_type='application/json')

    message = payload.get('message')
    if not message:
        return HttpResponseBadRequest(json.dumps({'error': 'Missing message field'}), content_type='application/json')

    # Minimal proxy: call Gemini REST endpoint. Replace with actual Gemini endpoint details.
    try:
        import requests
        endpoint = os.environ.get('GEMINI_ENDPOINT', 'https://api.gemini.example/v1/chat')
        headers = {
            'Authorization': f'Bearer {GEMINI_API_KEY}',
            'Content-Type': 'application/json'
        }
        body = {
            'input': message,
            'model': os.environ.get('GEMINI_MODEL', 'gemini-default')
        }
        resp = requests.post(endpoint, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Expect data to contain a 'reply' or similar field — adapt depending on API
        reply = data.get('reply') or data.get('output') or data
        return JsonResponse({'reply': reply})
    except Exception as e:
        return HttpResponseServerError(json.dumps({'error': str(e)}), content_type='application/json')
