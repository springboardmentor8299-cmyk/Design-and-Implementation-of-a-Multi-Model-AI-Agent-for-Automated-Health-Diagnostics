document.getElementById("form").addEventListener("submit", async function(e){

    e.preventDefault();

    let formData = new FormData();

    formData.append("file", document.getElementById("file").files[0]);
    formData.append("age", document.getElementById("age").value);

    // 🔥 ADD LIFESTYLE INPUTS
    formData.append("exercise", document.getElementById("exercise").value);
    formData.append("smoking", document.getElementById("smoking").value);
    formData.append("sleep", document.getElementById("sleep").value);

    // 🔥 CALL FASTAPI BACKEND
    let response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData
    });

    let data = await response.json();

    if (!data.success) {
        alert("Error: " + data.error);
        return;
    }

    let result = document.getElementById("result");

    // 🔥 PARAMETERS TABLE
    let tableRows = Object.keys(data.data).map(p => `
        <tr>
            <td>${p}</td>
            <td>${data.data[p]}</td>
        </tr>
    `).join("");

    // 🔥 RISKS
    let risksHTML = data.risks.map(r => `
        <div>
            <b>${r.name}</b> (${r.level}) - Score: ${r.score}<br>
            ${r.reason}
        </div>
    `).join("<br>");

    // 🔥 RECOMMENDATIONS
    let recHTML = data.recommendations.join("<br>");

    // 🔥 FINAL UI
    result.innerHTML = `
        <h2>Health Score: ${data.score}</h2>

        <h3>Parameters</h3>
        <table border="1">
            <tr><th>Parameter</th><th>Value</th></tr>
            ${tableRows}
        </table>

        <h3>Risks</h3>
        ${risksHTML}

        <h3>Recommendations</h3>
        ${recHTML}
    `;
});