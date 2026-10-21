"""Read the selected Connect target without displaying credentials or server URLs."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def main():
    server = os.environ.get('CONNECT_SERVER', '').rstrip('/')
    key = os.environ.get('CONNECT_API_KEY', '')
    guid = os.environ.get('CONTENT_GUID', '')
    confirmed = os.environ.get('CONFIRMED_CONTENT_TITLE', '')
    if not server or not key or not guid or guid == 'PUT_GUID_HERE':
        sys.exit('ERROR: Set CONNECT_SERVER/CONNECT_API_KEY secrets and CONNECT_CONTENT_GUID repository variable')
    if not server.startswith('https://'):
        sys.exit('ERROR: CONNECT_SERVER must use HTTPS')
    if not confirmed:
        sys.exit('ERROR: Human confirmation of the content title is required')
    request = urllib.request.Request(server + '/__api__/v1/content/' + urllib.parse.quote(guid, safe=''),
                                     headers={'Authorization': 'Key ' + key})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = json.load(response)
    except (urllib.error.URLError, ValueError):
        sys.exit('ERROR: Unable to read Connect target; check secrets, GUID and publisher access')
    title = content.get('title') or content.get('name')
    print('Target title:', title)
    print('Target GUID:', guid)
    if title != confirmed:
        sys.exit('ERROR: Target title differs from the title confirmed by the human')
    if content.get('access_type') != 'all':
        sys.exit('ERROR: Target is not public; a human must configure public access for the judges')
    print('PASS: confirmed target title and public access; no changes made')


if __name__ == '__main__':
    main()
