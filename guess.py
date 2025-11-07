from fastapi.responses import JSONResponse
from flask import Blueprint, jsonify, request
from playerCheck import get_random_player_id_and_name
import playerCheck

import random
from fastapi.responses import JSONResponse

def get_journeyman(max_attempts: int = 100):
    """Return a random NHL player who has played for at least 5 teams."""
    for _ in range(max_attempts):
        # Fetch a random player (batched)
        player_id, name = get_random_player_id_and_name(limit=50, max_attempts=10)
        if not name:
            continue  # Try again if API failed
        # Check if the player has played for at least 5 teams
        teams_played = playerCheck.get_nhl_teams_played(player_id)
        if len(teams_played) >= 5:
            print(name)
            return name, teams_played

    # If no journeyman found after max_attempts
    return JSONResponse({"result": "notFound"}, status_code=404)

