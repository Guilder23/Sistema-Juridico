import os
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_google_credential_from_user(user):
    if not user or not user.is_authenticated:
        raise ValueError('El usuario debe estar autenticado.')

    social_account = user.socialaccount_set.filter(provider='google').first()
    if not social_account:
        raise ValueError('El usuario no tiene una cuenta de Google asociada.')

    extra_data = social_account.extra_data or {}
    access_token = extra_data.get('access_token')
    refresh_token = extra_data.get('refresh_token')

    if not access_token:
        raise ValueError('No hay token de acceso de Google para este usuario.')

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
