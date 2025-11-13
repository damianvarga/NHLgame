let currentDuel = null;

async function fetchDuel() {
    const res = await fetch("/api/duel");
    const data = await res.json();
    currentDuel = data;

    const statName = { goals: "goals", assists: "assists", points: "points" }[data.stat];
    document.getElementById("question").textContent =
        `Who registered more ${statName} in the ${data.player1.season} season?`;

    document.getElementById("p1").textContent = data.player1.name;
    document.getElementById("p2").textContent = data.player2.name;

    document.getElementById("result").textContent = "";
    document.getElementById("next").classList.add("hidden");
}

function checkAnswer(choice) {
    const stat = currentDuel.stat;
    const p1 = currentDuel.player1[stat];
    const p2 = currentDuel.player2[stat];
    const correct =
        (choice === "p1" && p1 > p2) ||
        (choice === "p2" && p2 > p1);

    const result = document.getElementById("result");
    if (correct) {
        result.textContent = "Correct!";
        result.style.color = "lime";
    } else {
        result.textContent = "Incorrect!";
        result.style.color = "red";
    }

    result.textContent += ` (${currentDuel.player1.name}: ${p1}, ${currentDuel.player2.name}: ${p2})`;
    document.getElementById("next").classList.remove("hidden");
}

document.getElementById("p1").addEventListener("click", () => checkAnswer("p1"));
document.getElementById("p2").addEventListener("click", () => checkAnswer("p2"));
document.getElementById("next").addEventListener("click", fetchDuel);

fetchDuel();
