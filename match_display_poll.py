import requests
from constants import *
from threading import Thread

_url = "https://frc.nexus/api/v1/event/" + NEXUS_EVENT_KEY
_headers = {"Nexus-Api-Key": NEXUS_API_KEY}

_current_score = 0
_in_match = False

_my_matches = None
_my_next_match = None

def _poll():
    response = requests.get(_url, headers=_headers)

    if not response.ok:
        error_message = response.text
        print("Error getting live event status: {}".format(error_message))

    data = response.json()

    while True:        
        _my_matches = filter(lambda m: FRC_TEAM_NUMBER in m.get('redTeams', []) + m.get('blueTeams', []), data['matches'])
        _my_next_match = next(filter(lambda m: not m['status'] == 'On field', _my_matches), None)

_polling_thread = Thread(target=_poll)

def get_score():
    return _current_score

def get_in_match():
    return _in_match

def get_next_match():
    return _my_next_match

def get_matches():
    return _my_matches

def start_poll():
    _polling_thread.start()