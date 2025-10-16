// Render underscores for letters in the player's name, preserving spaces and punctuation.
document.addEventListener("DOMContentLoaded", async () => {

  const displayEl = document.querySelector(".word-display");
  if (!displayEl) return;

  displayEl.setAttribute("aria-live", "polite");
  displayEl.textContent = "Loading player...";

  let name = null;
  try {
    const res = await fetch("/api/random-player", { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    const data = await res.json();
    name = (data && data.name) || null;
  } catch (e) {
    console.warn("Falling back to default name due to API error:", e);
    name = "Sidney Crosby"; // fallback so the UI still demonstrates behavior
  }

  if (!name) {
    displayEl.textContent = "Failed to load player. Please refresh.";
    return;
  }

  displayEl.dataset.playerName = name;

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
      span.dataset.letter = ch.toUpperCase();
      span.textContent = "_";
      frag.appendChild(span);
    } else {
      // Preserve punctuation or special characters
      const span = document.createElement("span");
      span.className = "char";
      span.textContent = ch;
      frag.appendChild(span);
    }
  }

  displayEl.appendChild(frag);
});

/**
 * Hangman front-end logic:
 * - Fetch random player from /api/random-player (falls back to "Sidney Crosby" if needed)
 * - Render underscores for letters, preserve spaces/punctuation
 * - On key click/press: reveal matching letters or decrement lives for misses
 * - Disable keys after use to avoid double-counting
 */
'use strict';

/**
 * Hangman front-end logic:
 * - Fetch random player from /api/random-player (fallback to "Sidney Crosby" if needed)
 * - Render underscores for letters, preserve spaces/punctuation
 * - On letter button click: reveal matching letters or decrement lives for misses
 * - Disable used keys to prevent double-counting
 */

document.addEventListener('DOMContentLoaded', () => {
  const MAX_LIVES = 5;

  let lives = MAX_LIVES;

  const displayEl = document.getElementById('word-display') || document.querySelector('.word-display');
  const counterEl = document.getElementById('error-counter');
  const keyboardEl = document.getElementById('keyboard');

  if (!displayEl) {
    console.error('word-display element not found.');
    return;
  }

  function updateCounter() {
    if (counterEl) {
      counterEl.textContent = `Lives left: ${lives}`;
    }
  }

  function disableAllKeys() {
    if (!keyboardEl) return;
    keyboardEl.querySelectorAll('button').forEach((btn) => {
      btn.disabled = true;
    });
  }

  function revealRemainingLetters() {
    displayEl.querySelectorAll('.char.masked').forEach((span) => {
      span.textContent = span.dataset.original || span.textContent;
      span.classList.remove('masked');
      span.classList.add('revealed');
    });
  }

  function isWordFullyRevealed() {
    return displayEl.querySelectorAll('.char.masked').length === 0;
  }

  function renderMasked(name) {
    // Build masked display:
    // - Letters -> "_" with data-letter=UPPER and data-original for reveal
    // - Spaces -> span.space-gap
    // - Other chars -> shown as-is
    displayEl.innerHTML = '';
    const frag = document.createDocumentFragment();

    for (const ch of name) {
      if (ch === ' ') {
        const gap = document.createElement('span');
        gap.className = 'space-gap';
        gap.textContent = ' ';
        frag.appendChild(gap);
      } else if (/[A-Za-z]/.test(ch)) {
        const span = document.createElement('span');
        span.className = 'char masked';
        span.dataset.letter = ch.toUpperCase();
        span.dataset.original = ch; // preserve original case
        span.textContent = '_';
        frag.appendChild(span);
      } else {
        const span = document.createElement('span');
        span.className = 'char';
        span.textContent = ch; // punctuation and other symbols are visible
        frag.appendChild(span);
      }
    }

    displayEl.appendChild(frag);
  }

  function revealLetter(letterUpper) {
    const matches = displayEl.querySelectorAll(`.char.masked[data-letter="${letterUpper}"]`);
    matches.forEach((span) => {
      span.textContent = span.dataset.original || letterUpper;
      span.classList.remove('masked');
      span.classList.add('revealed');
    });
    return matches.length;
  }

  async function fetchRandomPlayerName() {
    try {
      const res = await fetch('/api/random-player', { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return (data && data.name) || null;
    } catch (err) {
      console.warn('Falling back to default name due to API error:', err);
      return 'Sidney Crosby';
    }
  }

  function attachClickHandlers() {
    if (!keyboardEl) return;

    keyboardEl.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;

      const letter = (btn.dataset.letter || btn.textContent || '').trim().toUpperCase();
      if (!letter || btn.disabled) return;

      const revealed = revealLetter(letter);

      if (revealed > 0) {
        // Correct guess
        btn.classList.add('correct', 'used');
        btn.disabled = true;

        if (isWordFullyRevealed()) {
          if (counterEl) counterEl.textContent = 'You win!';
          disableAllKeys();
        }
      } else {
        // Miss
        lives = Math.max(0, lives - 1);
        updateCounter();
        btn.classList.add('wrong', 'used');
        btn.disabled = true;

        if (lives === 0) {
          if (counterEl) counterEl.textContent = 'Game over!';
          revealRemainingLetters();
          disableAllKeys();
        }
      }
    });
  }

  async function bootstrap() {
    displayEl.setAttribute('aria-live', 'polite');
    displayEl.textContent = 'Loading player...';
    updateCounter();
    attachClickHandlers();

    const name = await fetchRandomPlayerName();
    renderMasked(name);
  }

  // Start after DOM is ready
  bootstrap();
});