// ── State ───────────────────────────────────────
let allTableRows = [];
let ipAnalysisData = {};

// ── Boot ────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("etcSecData");

  if (!raw) return;

  try {
    const sec = JSON.parse(raw);
    showResults(sec);

    const ts = sessionStorage.getItem("etcScanTime");
    if (ts) {
      document.getElementById("lastScanTime").textContent = ts;
    }
  } catch (e) {
    console.error("Parse error:", e);
  }
});

// ── Show results ─────────────────────────────────
function showResults(sec) {
  document.getElementById("noDataBanner").style.display = "none";
  document.getElementById("threatResults").style.display = "block";

  ipAnalysisData = sec.ip_analysis || {};
  const riskDist = sec.risk_distribution || { High: 0, Medium: 0, Low: 0 };
  const overall = sec.overall_risk || "Low";
  const suspicious = sec.suspicious_entities || [];

  // Overall risk pill
  const pill = document.getElementById("overallRiskPill");
  pill.className = "overall-risk-pill risk-" + overall.toLowerCase();
  document.getElementById("overallRiskLabel").textContent =
    overall.toUpperCase() + " RISK";

  // KPI
  document.getElementById("highCount").textContent = riskDist.High || 0;
  document.getElementById("medCount").textContent = riskDist.Medium || 0;
  document.getElementById("lowCount").textContent = riskDist.Low || 0;
  document.getElementById("entityCount").textContent =
    Object.keys(ipAnalysisData).length;

  renderSuspiciousEntities(suspicious);
  renderRiskTypeBreakdown(ipAnalysisData);
  buildTableRows(ipAnalysisData);
  filterTable();
}

// ── Suspicious entities ──────────────────────────
function renderSuspiciousEntities(suspicious) {
  const wrap = document.getElementById("suspiciousEntities");

  if (!suspicious.length) {
    wrap.innerHTML = `<div class="results-empty">No high-risk entities</div>`;
    return;
  }

  const items = suspicious.map(id => {
    const e = ipAnalysisData[id] || {};

    return `
      <div class="suspicious-item">
        <div>
          <div><b>${id}</b></div>
          <div>${e.traffic || "Unknown"}</div>
          <div style="font-size:0.8rem;color:#888;">
            ${e.malicious || "Benign"} • ${e.confidence || 0}% confidence
          </div>
        </div>
        <span class="risk-badge high">HIGH</span>
      </div>
    `;
  }).join("");

  wrap.innerHTML = items;
}

// ── Risk breakdown ───────────────────────────────
function renderRiskTypeBreakdown(ipAnalysis) {

  const wrap = document.getElementById("riskTypeBreakdown");
  const typeRisk = {};

  for (const e of Object.values(ipAnalysis)) {
    const t = e.traffic || "Unknown";

    if (!typeRisk[t]) typeRisk[t] = { High: 0, Medium: 0, Low: 0 };

    typeRisk[t][e.risk]++;
  }

  wrap.innerHTML = Object.entries(typeRisk).map(([label, r]) => `
    <div style="margin-bottom:10px;">
      <b>${label}</b> → 
      <span style="color:red;">H:${r.High}</span> 
      <span style="color:orange;">M:${r.Medium}</span> 
      <span style="color:green;">L:${r.Low}</span>
    </div>
  `).join("");
}

// ── Table ───────────────────────────────────────
function buildTableRows(ipAnalysis) {

  const order = { High: 0, Medium: 1, Low: 2 };

  allTableRows = Object.entries(ipAnalysis)
    .map(([id, e]) => ({
      id,
      traffic: e.traffic || "Unknown",
      malicious: e.malicious || "Benign",
      confidence: Number(e.confidence || 0),
      flowCount: e.flowCount || 1,
      risk: e.risk || "Low"
    }))
    .sort((a, b) => (order[a.risk] ?? 2) - (order[b.risk] ?? 2));

  document.getElementById("tableCountBadge").textContent =
    allTableRows.length + " entities";
}

// ── Filter ──────────────────────────────────────
function filterTable() {

  const filter = document.getElementById("riskFilter").value;

  const rows = filter === "all"
    ? allTableRows
    : allTableRows.filter(r => r.risk === filter);

  const wrap = document.getElementById("entityTableWrap");

  if (!rows.length) {
    wrap.innerHTML = `<div class="results-empty">No data</div>`;
    return;
  }

  const getRiskClass = r => {
    if (r === "High") return "high";
    if (r === "Medium") return "medium";
    return "low";
  };

  const getMalClass = m => {
    return m === "Malicious" ? "high" : "low";
  };

  wrap.innerHTML = `
    <table class="entity-table">
      <thead>
        <tr>
          <th>Entity</th>
          <th>Traffic</th>
          <th>Malicious</th>
          <th>Confidence</th>
          <th>Risk</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => `
          <tr>
            <td><b>${r.id}</b></td>

            <td>
              <span class="traffic-mini-tag">${r.traffic}</span>
            </td>

            <td>
              <span class="risk-badge ${getMalClass(r.malicious)}">
                ${r.malicious}
              </span>
            </td>

            <td>
              <span style="font-weight:600;">
                ${r.confidence.toFixed(2)}%
              </span>
            </td>

            <td>
              <span class="risk-badge ${getRiskClass(r.risk)}">
                ${r.risk.toUpperCase()}
              </span>
            </td>

          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}