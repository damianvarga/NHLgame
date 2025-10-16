document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("td").forEach(cell => {
        cell.addEventListener("click", async () => {
            let playerName = prompt("Enter player name:");
            if (!playerName) return;

            let response = await fetch("/check-player", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: playerName,
                    row_team: cell.getAttribute("data-row-team"),
                    col_team: cell.getAttribute("data-col-team")
                })
            });

            let data = await response.json();

            // Ak hráč pasuje, zapíš meno do bunky
            if (data.result !== "Incorrect" && data.result !== "Used" && data.result !== "notFound") {
                console.log(data.result)

                cell.innerHTML = data.result;
            } else if (data.result === "Incorrect"){
                alert("Incorrect!");
            } else if (data.result === "Used") {
                alert("Played already used!");
            }else {
                alert("Player not found!")
            }
        });
    });
});
