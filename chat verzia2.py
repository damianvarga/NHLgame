import csv
import requests
import re

def played_for_any_season(player_slug, team_slug):
    """
    Overí, či hráč hral niekedy za daný tím podľa hockey.db (z GitHub-u).
    """
    api_url = f"https://api.github.com/repos/open-sports/hockey.db/contents/leagues/nhl/teams/{team_slug}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    # Získaj zoznam súborov v adresári tímu
    resp = requests.get(api_url, headers=headers)
    print(resp.status_code)
    if resp.status_code != 200:
        return False

    files = resp.json()
    csv_files = [f["name"] for f in files if f["name"].endswith(".csv")]
    print(files)
    # Prejdi každú sezónu
    for filename in csv_files:
        raw_url = f"https://raw.githubusercontent.com/open-sports/hockey.db/master/leagues/nhl/teams/{team_slug}/{filename}"
        try:
            r = requests.get(raw_url)
            print(r.status_code)
            if r.status_code == 200:
                if re.search(player_slug.lower(), r.text.lower()):
                    return True
        except:
            continue
    return False

print(played_for_any_season("artemi-panarin", "nyr"))         # True
print(played_for_any_season("artemi-panarin", "chicago"))    # True
print(played_for_any_season("artemi-panarin", "philadelphia"))# False


document.addEventListener("DOMContentLoaded", async () => {
  const displayEl = document.querySelector(".word-display");
  if (!displayEl) return;

  // Optional accessibility announcement
  displayEl.setAttribute("aria-live", "polite");

  // Loading state
  displayEl.textContent = "Loading player...";

  try {
    const res = await fetch("/api/random-player", { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    const data = await res.json();
    const name = (data && data.name) || "";

    // Store original name for future game logic
    displayEl.dataset.playerName = name;

    // Build masked display:
    // - Letters -> "_"
    // - Spaces -> preserved as a visual gap
    // - Other chars (e.g., hyphens, apostrophes) -> preserved
    displayEl.innerHTML = "";
    const frag = document.createDocumentFragment();

    for (const ch of name) {
      if (ch === " ") {
        const gap = document.createElement("span");
        gap.className = "space-gap";
        gap.textContent = " ";
        frag.appendChild(gap);
      } else if (/[A-Za-z]/.test(ch)) {
        const span = document.createElement("span");
        span.className = "char";
        span.textContent = "_";
        frag.appendChild(span);
      } else {
        // Preserve punctuation or other symbols as-is
        const span = document.createElement("span");
        span.className = "char";
        span.textContent = ch;
        frag.appendChild(span);
      }
    }

    displayEl.appendChild(frag);
  } catch (err) {
    console.error(err);
    displayEl.textContent = "Failed to load player. Please refresh.";
  }
});