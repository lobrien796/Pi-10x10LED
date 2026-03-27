import datetime
import requests
import sys
from constants import *

url = "https://frc.nexus/api/v1/event/" + NEXUS_EVENT_KEY

headers = {"Nexus-Api-Key": NEXUS_API_KEY}

def _getData():
  response = requests.get(url, headers=headers)

  if not response.ok:
    error_message = response.text
    print("Error getting live event status: {}".format(error_message))

  data = response.json()

  return data

# while True:
data = _getData()
print(data)

# Get information about a specific team's next match.
my_matches = filter(lambda m: FRC_TEAM_NUMBER in m.get('redTeams', []) + m.get('blueTeams', []), data['matches'])
my_next_match = next(filter(lambda m: not m['status'] == 'On field', my_matches), None)

if my_next_match:
  print("Team {}'s next match is {} ({})!".format(FRC_TEAM_NUMBER, my_next_match['label'], my_next_match['status']))

  alliance_color = 'red' if FRC_TEAM_NUMBER in my_next_match.get('redTeams', []) else 'blue'
  print("Put on the {} bumpers".format(alliance_color))

  estimated_queue_time = my_next_match['times'].get('estimatedQueueTime', None)
  if estimated_queue_time:
    print("We will be queued at ~{}".format(datetime.datetime.fromtimestamp(estimated_queue_time / 1000)))
else:
  print("Team {} doesn't have any future matches scheduled yet".format(FRC_TEAM_NUMBER))

# Get announcements and parts requests.
for announcement in data['announcements']:
  print("Event announcement: {}".format(announcement['announcement']))