import requests
import ast
import json
import random
import string
from typing import Optional, Tuple, Dict, Any

def search_player(name):
    url = f"https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=10&q=\"{name}\""
    res = requests.get(url)
    print("Status Code:", res.status_code)
    print("Response Text:", res.text)
    resArray = json.loads(res.text)
    if resArray and isinstance(resArray, list):
        if len(resArray) == 1:
            return resArray[0]
        else:
            print("Choose a player you want")
            for i, player in enumerate(resArray):
                print(f"{i+1}. {player['name']} \
                \n position. {player['positionCode']} \
                \n country {player['birthCountry']} ")
                if player.get('lastSeasonId'):
                    # lastSeasonId is usually a string like "20232024"
                    print(f"last season: {player['lastSeasonId']} \n")
            choiceIndex = int(input())
            return resArray[choiceIndex-1]
    return None


def get_nhl_teams_played(player_id):
    """Zistí, za ktoré NHL tímy hráč hral (iba NHL kariéra)"""
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"

    resStr = requests.get(url)
    res = json.loads(resStr.text)

    nhl_teams = set()
    try:
        for season in res['seasonTotals']:
            if season['leagueAbbrev'] == 'NHL':
                nhl_teams.add(season['teamName']['default'])
    except Exception:
        pass

    return nhl_teams


def _extract_player_id(p: Dict[str, Any]) -> Optional[int]:
    """Extract player ID from a search result item with varying field names."""
    for key in ("id", "playerId", "personId"):
        if key in p and p[key] is not None:
            try:
                return int(p[key])
            except (TypeError, ValueError):
                continue
    return None


def _extract_player_name(p: Dict[str, Any]) -> Optional[str]:
    """Extract a displayable player name from a search result item."""
    if 'name' in p and p['name']:
        return p['name']
    first = p.get('firstName') or p.get('first_name')
    last = p.get('lastName') or p.get('last_name')
    if first or last:
        return f"{first or ''} {last or ''}".strip() or None
    return None


def get_random_player_id_and_name(limit: int = 50, max_attempts: int = 10) -> Optional[Tuple[int, str]]:
    """
    Vyhľadá náhodného hráča pomocou NHL search API a vráti jeho (id, meno).

    Strategy:
    - Pick a random lowercase letter.
    - Query the search API with that letter to get up to `limit` players.
    - Randomly select one player from the results.
    - Extract and return (player_id, player_name).

    Returns:
        (player_id, player_name) or None if no player could be found.
    """
    letters = string.ascii_lowercase

    for attempt in range(max_attempts):
        q = random.choice(letters)
        url = f"https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit={limit}&q={q}"
        try:
            res = requests.get(url, timeout=10)
        except requests.RequestException as e:
            print(f"[Attempt {attempt+1}/{max_attempts}] Request error: {e}")
            continue

        if res.status_code != 200:
            print(f"[Attempt {attempt+1}/{max_attempts}] Bad status {res.status_code} for q={q}")
            continue

        try:
            results = json.loads(res.text)
        except json.JSONDecodeError as e:
            print(f"[Attempt {attempt+1}/{max_attempts}] JSON decode error: {e}")
            continue

        if not isinstance(results, list) or len(results) == 0:
            print(f"[Attempt {attempt+1}/{max_attempts}] No results for q={q}")
            continue

        candidate = random.choice(results)
        pid = _extract_player_id(candidate)
        pname = _extract_player_name(candidate)

        if pid is not None and pname:
            return pid, pname

        # If extraction failed, try another attempt
        print(f"[Attempt {attempt+1}/{max_attempts}] Could not extract id/name from candidate: {candidate}")

    return None


from flask import Blueprint, jsonify
from playerCheck import get_random_player_id_and_name

random_player_api = Blueprint("random_player_api", __name__)

@random_player_api.route("/api/random-player", methods=["GET"])
def get_random_player():
    """
    Returns a random NHL player as JSON:
    {
      "id": <int>,
      "name": <str>
    }
    """
    result = get_random_player_id_and_name()
    if not result:
        return jsonify({"error": "no_player_found"}), 503

    player_id, player_name = result
    return jsonify({"id": player_id, "name": player_name})