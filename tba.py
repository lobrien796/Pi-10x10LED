import time
import threading
import requests
from utils import (
    match_active, match_state, match_lock,
    GRID_W, GRID_H, show_grid, clear
)
from constants import TBA_API_KEY, TBA_EVENT_KEY, FRC_TEAM_NUMBER

TBA_BASE = "https://www.thebluealliance.com/api/v3"
POLL_INTERVAL = 5  # seconds

def _headers():
    return {"X-TBA-Auth-Key": TBA_API_KEY}

def _team_key():
    return f"frc{FRC_TEAM_NUMBER}"

def _get(endpoint):
    try:
        r = requests.get(f"{TBA_BASE}{endpoint}", headers=_headers(), timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"TBA request failed: {e}")
    return None

def _find_our_alliance(match):
    """Return ("red"|"blue", score, opponent_score) or None if we're not in this match."""
    tk = _team_key()
    alliances = match.get("alliances", {})
    for color in ("red", "blue"):
        teams = alliances.get(color, {}).get("team_keys", [])
        if tk in teams:
            our_score   = alliances[color].get("score", 0)
            other_color = "blue" if color == "red" else "red"
            their_score = alliances.get(other_color, {}).get("score", 0)
            return color, our_score, their_score
    return None

def _is_match_live(match):
    """True if the match has started but not yet been officially scored."""
    # TBA sets score to -1 while a match is in progress
    alliances = match.get("alliances", {})
    red_score  = alliances.get("red",  {}).get("score", -1)
    blue_score = alliances.get("blue", {}).get("score", -1)
    return red_score == -1 or blue_score == -1

def tba_listener():
    """Background thread — polls TBA every POLL_INTERVAL seconds."""
    # Silently do nothing if credentials/event aren't configured
    if not TBA_API_KEY or not TBA_EVENT_KEY:
        print("TBA: API key or event key not set — match detection disabled.")
        return

    print(f"TBA listener started for event {TBA_EVENT_KEY}, team {FRC_TEAM_NUMBER}.")

    while True:
        matches = _get(f"/event/{TBA_EVENT_KEY}/matches")
        found_live = False

        if matches:
            for match in matches:
                result = _find_our_alliance(match)
                if result is None:
                    continue  # we're not in this match

                color, our_score, their_score = result

                if _is_match_live(match):
                    with match_lock:
                        match_state["our_alliance"] = color
                        match_state["our_score"]    = max(our_score, 0)
                        match_state["their_score"]  = max(their_score, 0)
                    if not match_active.is_set():
                        print(f"TBA: Match live! We are {color}. Setting match_active.")
                        match_active.set()
                    found_live = True
                    break  # only care about the first live match we're in

        if not found_live and match_active.is_set():
            print("TBA: Match no longer live. Clearing match_active.")
            match_active.clear()

        time.sleep(POLL_INTERVAL)