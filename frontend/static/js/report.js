document.addEventListener("DOMContentLoaded", () => {

  const raw = sessionStorage.getItem("multiModelResults");

  if (!raw) {
    console.warn("No data found in sessionStorage");
    return;
  }

  let data;

  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.error("Invalid JSON in sessionStorage", e);
    return;
  }

  const models = ["rf", "xgb", "lgbm"];

  let html = `
    <table class="entity-table">
      <thead>
        <tr>
          <th>Model</th>
          <th>Accuracy</th>
          <th>Precision</th>
          <th>Recall</th>
          <th>F1 Score</th>
        </tr>
      </thead>
      <tbody>
  `;

  models.forEach(m => {

    // ✅ Support both formats (old + slim)
    const metrics = data[m]?.metrics || data[m] || {};

    html += `
      <tr>
        <td>${m.toUpperCase()}</td>
        <td>${((metrics.accuracy || 0) * 100).toFixed(2)}%</td>
        <td>${((metrics.precision || 0) * 100).toFixed(2)}%</td>
        <td>${((metrics.recall || 0) * 100).toFixed(2)}%</td>
        <td>${((metrics.f1 || 0) * 100).toFixed(2)}%</td>
      </tr>
    `;
  });

  html += `</tbody></table>`;

  const tableContainer = document.getElementById("comparisonTable");

  if (tableContainer) {
    tableContainer.innerHTML = html;
  } else {
    console.warn("comparisonTable element not found");
  }

});