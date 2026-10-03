import os
from datetime import datetime

from allauth.socialaccount.models import SocialToken
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def persist_google_social_token(social_account, token_obj=None):
    if not social_account or social_account.provider != 'google':
        return None

    if SocialToken.objects.filter(account=social_account).exists():
        return SocialToken.objects.get(account=social_account)

    token_value = None
    refresh_token = None
    expires_at = None

    if token_obj is not None:
        token_value = getattr(token_obj, 'token', None)
        refresh_token = getattr(token_obj, 'token_secret', None)
        expires_at = getattr(token_obj, 'expires_at', None)

    if token_value is None:
        extra_data = social_account.extra_data or {}
        token_value = extra_data.get('access_token') or extra_data.get('token')
        refresh_token = extra_data.get('refresh_token')

    if not token_value:
        return None

    return SocialToken.objects.create(
        account=social_account,
        token=token_value,
        token_secret=refresh_token or '',
        expires_at=expires_at,
    )


def get_google_account(user):
    if not user or not user.is_authenticated:
        return None
    return user.socialaccount_set.filter(provider='google').first()


def get_google_access_token(social_account):
    if not social_account:
        return None

    extra_data = social_account.extra_data or {}
    access_token = extra_data.get('access_token') or extra_data.get('token')
    if access_token:
        return access_token, extra_data.get('refresh_token')

    token = SocialToken.objects.filter(account=social_account).order_by('-expires_at').first()
    if token and token.token:
        return token.token, token.token_secret

    return None, None


def get_google_credential_from_user(user):
    if not user or not user.is_authenticated:
        raise ValueError('El usuario debe estar autenticado.')

    social_account = get_google_account(user)
    if not social_account:
        raise ValueError('El usuario no tiene una cuenta de Google asociada.')

    access_token, refresh_token = get_google_access_token(social_account)
    if not access_token:
        raise ValueError(
            'La cuenta de Google está vinculada, pero no hay un token válido. '
            'Vuelve a iniciar sesión con Google para autorizar Calendar, Drive y Docs.'
        )

    return Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
        scopes=[
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents',
        ],
    )


def get_google_account_connected(user):
    if not user or not user.is_authenticated:
        return False

    social_account = get_google_account(user)
    if not social_account:
        return False

    access_token, _ = get_google_access_token(social_account)
    return bool(access_token)


def list_google_calendar_events(user, limit=5):
    creds = get_google_credential_from_user(user)
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().strftime('%Y-%m-%dT00:00:00Z')

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=limit,
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    events = events_result.get('items', [])
    result = []
    for event in events:
        start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        end = event.get('end', {}).get('dateTime') or event.get('end', {}).get('date')
        result.append({
            'id': event.get('id'),
            'summary': event.get('summary') or 'Sin título',
            'start': start,
            'end': end,
            'html_link': event.get('htmlLink'),
        })
    return result


def list_google_drive_documents(user, limit=5):
    creds = get_google_credential_from_user(user)
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        pageSize=limit,
        fields='files(id, name, webViewLink, modifiedTime, mimeType)',
        q="trashed=false and (mimeType='application/vnd.google-apps.document' or mimeType='application/pdf' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.presentation')",
        orderBy='modifiedTime desc',
    ).execute()

    files = results.get('files', [])
    return [
        {
            'id': item.get('id'),
            'name': item.get('name') or 'Documento sin nombre',
            'modifiedTime': item.get('modifiedTime'),
            'webViewLink': item.get('webViewLink'),
        }
        for item in files
    ]


def create_google_calendar_event(user, title, start_iso, end_iso, description=''):
    creds = get_google_credential_from_user(user)
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_iso, 'timeZone': 'America/La_Paz'},
        'end': {'dateTime': end_iso, 'timeZone': 'America/La_Paz'},
    }

    return service.events().insert(calendarId='primary', body=event).execute()


def create_google_docs_document(user, title, content):
    creds = get_google_credential_from_user(user)
    docs_service = build('docs', 'v1', credentials=creds)

    document = docs_service.documents().create(body={'title': title}).execute()
    document_id = document['documentId']

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={
            'requests': [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content,
                    }
                }
            ]
        }
    ).execute()

    return document
