import time
import random
import string
from typing import Optional, Tuple, List

import requests
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import playerCheck

# Run: uvicorn main:app --reload --port 8000

app = FastAPI()

# Global game state for your grid page (unchanged)
grid_size = 3
used_players = set()

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates
templates = Jinja2Templates(directory="templates")

TEAMS_ABBREVS = [
    "ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL",
    "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR",
    "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WPG", "WSH", "UTA"
]
TEAMS = [
    "Anaheim Ducks",
    "Arizona Coyotes",
    "Boston Bruins",
    "Buffalo Sabres",
    "Calgary Flames",
    "Carolina Hurricanes",
    "Chicago Blackhawks",
    "Colorado Avalanche",
    "Columbus Blue Jackets",
    "Dallas Stars",
    "Detroit Red Wings",
    "Edmonton Oilers",
    "Florida Panthers",
    "Los Angeles Kings",
    "Minnesota Wild",
    "Montréal Canadiens",
    "Nashville Predators",
    "New Jersey Devils",
    "New York Islanders",
    "New York Rangers",
    "Ottawa Senators",
    "Philadelphia Flyers",
    "Pittsburgh Penguins",
    "San Jose Sharks",
    "Seattle Kraken",
    "St. Louis Blues",
    "Tampa Bay Lightning",
    "Toronto Maple Leafs",
    "Utah Mammoth",
    "Vancouver Canucks",
    "Vegas Golden Knights",
    "Washington Capitals",
    "Winnipeg Jets"
]

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    global grid_size
    row_teams = random.sample(TEAMS, grid_size)
    col_teams = random.sample([t for t in TEAMS if t not in row_teams], grid_size)
    rows_with_index = list(enumerate(row_teams))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "row_teams": rows_with_index,
        "col_teams": col_teams,
        "size": grid_size,
        "timestamp": int(time.time())  # cache busting
    })

@app.post("/check-player")
async def check_player(request: Request):
    data = await request.json()
    name = data.get("name")
    global used_players
    print("Used players", used_players)
    player = playerCheck.search_player(name)
    if not player:
        print("Player not found.")
        result = "notFound"
        return JSONResponse({"result": result})

    player_id = player['playerId']
    teams_played = playerCheck.get_nhl_teams_played(player_id)
    teams_played = check_defunct(teams_played)
    required_teams = {data.get("row_team"), data.get("col_team")}
    print(data.get("row_team"))
    print(f"Find a player: {player['name']}")
    print(f"Teams he played for: {', '.join(teams_played)}")
    if player["playerId"] in used_players:
        result = "Used"
    elif required_teams.issubset(teams_played):
        result = player['name']
        used_players.add(player_id)
    else:
        result = "Incorrect"

    return JSONResponse({"result": result})

def check_defunct(teams_played):
    if teams_played.issuperset({'Phoenix Coyotes'}) or teams_played.issuperset({'Winnipeg Jets (1979)'}):
        teams_played.add('Arizona Coyotes')
    if teams_played.issuperset({'Mighty Ducks of Anaheim'}):
        teams_played.add('Anaheim Ducks')
    if teams_played.issuperset({'Atlanta Flames'}):
        teams_played.add('Calgary Flames')
    if teams_played.issuperset({'Hartford Whalers'}):
        teams_played.add('Carolina Hurricanes')
    if teams_played.issuperset({'Chicago Black Hawks'}):
        teams_played.add('Chicago Blackhawks')
    if teams_played.issuperset({'Quebec Nordiques'}):
        teams_played.add('Colorado Avalanche')
    if teams_played.issuperset({'Minnesota North Stars'}):
        teams_played.add('Dallas Stars')
    if teams_played.issuperset({'Colorado Rockies'}) or teams_played.issuperset({'Kansas City Scouts'}):
        teams_played.add('New Jersey Devils')
    if teams_played.issuperset({'Atlanta Thrashers'}):
        teams_played.add('Winnipeg Jets')
    return teams_played

@app.post("/new-game/{n}")
def new_game(n: int):
    global used_players, grid_size
    used_players.clear()
    used_players = set()  # clear previously used players
    grid_size = n         # set new grid size
    return {"status": "new game", "size": n}

# ---------- Hangman additions ----------

router = APIRouter(tags=["hangman"])

# Curated fallback list so we always return a player even if the NHL API fails
FALLBACK_PLAYERS: List[str] = [
    "Sidney Crosby", "Connor McDavid", "Nathan MacKinnon", "Auston Matthews", "Leon Draisaitl",
    "Alex Ovechkin", "Nikita Kucherov", "David Pastrnak", "Cale Makar", "Mikko Rantanen",
    "Steven Stamkos", "Victor Hedman", "Erik Karlsson", "Jack Eichel", "Artemi Panarin",
    "Brad Marchand", "Patrick Kane", "Jonathan Toews", "Anze Kopitar", "Mark Stone",
    "Ilya Sorokin", "Igor Shesterkin", "Andrei Vasilevskiy", "William Nylander", "Mitch Marner",
    "Matthew Tkachuk", "Aleksander Barkov", "Kirill Kaprizov", "Jason Robertson", "Elias Pettersson"
]

def _extract_player_id(item) -> Optional[int]:
    for key in ("id", "playerId", "personId"):
        if key in item and item[key] is not None:
            try:
                return int(item[key])
            except (TypeError, ValueError):
                continue
    return None

def _extract_player_name(item) -> Optional[str]:
    if item.get("name"):
        return item["name"]
    first = item.get("firstName") or item.get("first_name")
    last = item.get("lastName") or item.get("last_name")
    name = f"{(first or '').strip()} {(last or '').strip()}".strip()
    return name or None

def get_random_player_id_and_name(limit: int = 50, max_attempts: int = 10) -> Optional[Tuple[int, str]]:
    """
    Query the NHL search API with random letters and return (id, name).
    Falls back to None if no player could be obtained.
    """
    letters = string.ascii_lowercase
    for _ in range(max_attempts):
        q = random.choice(letters)
        url = f"https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit={limit}&q={q}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            results = resp.json()
            if not isinstance(results, list) or not results:
                continue
            candidate = random.choice(results)
            pid = _extract_player_id(candidate)
            name = _extract_player_name(candidate)
            if pid and name:
                return pid, name
        except Exception:
            continue
    return None

@router.get("/api/random-player")
def api_random_player():
    """
    Returns a random NHL player as JSON: {"id": int|None, "name": str}
    Tries NHL API first; if unavailable, returns a random name from a fallback list with id=None.
    """
    result = get_random_player_id_and_name()
    if result:
        pid, pname = result
        return {"id": pid, "name": pname}

    # Fallback so the UI always works, even without external network
    fallback_name = random.choice(FALLBACK_PLAYERS)
    return {"id": None, "name": fallback_name}

@router.get("/hangman", response_class=HTMLResponse)
def hangman(request: Request):
    """
    Render the Hangman page (templates/hangman.html).
    Requires that your template links static assets using:
      <link rel="stylesheet" href="{{ url_for('static', path='/styles.css') }}">
      <script src="{{ url_for('static', path='/hangman.js') }}" defer></script>
    """
    return templates.TemplateResponse("hangman.html", {"request": request})

# Make sure the app actually uses the router (this is what was missing)
app.include_router(router)