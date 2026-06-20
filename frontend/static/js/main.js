/* =====================================================
   GLOBAL STATE
===================================================== */

let selectedModel = "rf";
let trafficChart = null;

const CHART_COLORS = [
  "#0057ff",
  "#00c4a7",
  "#ffaa00",
  "#ff3b5c",
  "#9b5cf6",
  "#06b6d4",
  "#f97316",
  "#84cc16"
];


/* =====================================================
   MODEL TOGGLE
===================================================== */

function selectModel(model) {

  selectedModel = model;

  document.getElementById("btnRF").classList.toggle("selected", model === "rf");
  document.getElementById("btnXGB").classList.toggle("selected", model === "xgb");
  document.getElementById("btnLGBM").classList.toggle("selected", model === "lgbm");

  const labels = {
    rf: "Random Forest",
    xgb: "XGBoost",
    lgbm: "LightGBM"
  };

  document.getElementById("sidebarModel").textContent = labels[model];
  document.getElementById("modelBadge").textContent = labels[model];

  setStep(2);
}


/* =====================================================
   FILE SELECTION
===================================================== */

function onFileChange(input){

  const fileSelected = document.getElementById("fileSelected");
  const fileName = document.getElementById("fileName");

  if(input.files.length){

    fileName.textContent = input.files[0].name;
    fileSelected.style.display = "flex";

    setStep(2);

  }else{

    fileSelected.style.display = "none";

  }

}


/* =====================================================
   STEP TRACKER
===================================================== */

function setStep(active){

  for(let i=1;i<=4;i++){

    const el = document.getElementById(`step${i}`);

    if(!el) continue;

    el.classList.remove("active","done");

    if(i < active) el.classList.add("done");
    if(i === active) el.classList.add("active");

  }

}


/* =====================================================
   UPLOAD + CLASSIFICATION
===================================================== */

function uploadFile(){

  const fileInput = document.getElementById("fileInput");

  if(!fileInput.files.length){

    alert("Please upload CSV file first");
    return;

  }

  const btn = document.getElementById("runBtn");

  btn.disabled = true;
  btn.classList.add("loading");

  btn.querySelector(".btn-text").textContent = "Classifying…";

  setStep(3);

  const formData = new FormData();

  formData.append("file", fileInput.files[0]);
  formData.append("model", selectedModel);

  fetch("/predict",{

    method:"POST",
    body:formData

  })
  .then(res=>res.json())
.then(data=>{

  console.log("SERVER RESPONSE", data);

  const { distribution, metrics, security } = data;

  if (!distribution) throw new Error("No distribution returned");

// 🔥 SAVE SECURITY DATA (SAFE VERSION)
if (security && Object.keys(security).length > 0) {

  try {

    // ✅ STORE COMPLETE SECURITY OBJECT (IMPORTANT)
    sessionStorage.setItem("etcSecData", JSON.stringify(security));

    const now = new Date().toLocaleTimeString();
    sessionStorage.setItem("etcScanTime", now);

  } catch (e) {
    console.error("Storage failed:", e);
  }

}

  window.dashboardData = {
    distribution,
    metrics,
    security
  };


    


    /* ---------------- CHART ---------------- */

    renderPieChart(distribution);


    /* ---------------- KPI ---------------- */

updateKPI("accuracy", metrics?.accuracy || 0);
updateKPI("precision", metrics?.precision || 0);
updateKPI("recall", metrics?.recall || 0);
updateKPI("f1", metrics?.f1 || 0);

    /* ---------------- SUMMARY ---------------- */

    const totalFlows = Object.values(distribution).reduce((a,b)=>a+b,0);

    const topTraffic = Object.entries(distribution)
      .sort((a,b)=>b[1]-a[1])[0];

    const topPct = ((topTraffic[1]/totalFlows)*100).toFixed(1);

    document.getElementById("totalFlowsBadge").textContent =
      `${totalFlows.toLocaleString()} total flows`;

    document.getElementById("results").innerHTML = `

      <div class="result-stat-grid">

        <div class="result-stat">
          <div class="result-stat-label">Total Flows</div>
          <div class="result-stat-value">${totalFlows.toLocaleString()}</div>
        </div>

        <div class="result-stat">
          <div class="result-stat-label">Dominant Traffic</div>
          <div class="result-stat-value">${topTraffic[0]}</div>
        </div>

        <div class="result-stat">
          <div class="result-stat-label">Dominant Share</div>
          <div class="result-stat-value">${topPct}%</div>
        </div>

        <div class="result-stat">
          <div class="result-stat-label">Traffic Classes</div>
          <div class="result-stat-value">${Object.keys(distribution).length}</div>
        </div>

      </div>
    `;

    setStep(4);

  })
  .catch(err=>{

    console.error(err);

    document.getElementById("results").innerHTML =
      `<p style="color:red">Error processing dataset</p>`;

  })
  .finally(()=>{

    btn.disabled = false;
    btn.classList.remove("loading");
    btn.querySelector(".btn-text").textContent = "Run Classification";

  });

}


/* =====================================================
   RUN ALL MODELS (GLOBAL FUNCTION)
===================================================== */

async function runAllModels(){

  const fileInput = document.getElementById("fileInput");

  if(!fileInput.files.length){
    alert("Please upload CSV file first");
    return;
  }

  const file = fileInput.files[0];
  const models = ["rf","xgb","lgbm"];

  let results = {};

  for(let m of models){

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", m);

    try{

      const res = await fetch("/predict",{
        method:"POST",
        body:formData
      });

      const data = await res.json();

      results[m] = data;

    }catch(err){

      console.error("Error in model:", m, err);

    }

  }

// SAVE ONLY SLIM DATA (SAFE)
const slimResults = {};

for (let m in results) {

  const data = results[m] || {};

  slimResults[m] = {
    accuracy: data.metrics?.accuracy || 0,
    precision: data.metrics?.precision || 0,
    recall: data.metrics?.recall || 0,
    f1: data.metrics?.f1 || 0
  };

}

try {
  sessionStorage.setItem("multiModelResults", JSON.stringify(slimResults));
} catch (e) {
  console.error("Storage failed:", e);
}

console.log("Saved slim results:", slimResults);

  // ENABLE BUTTON
  enableReportButton();

}


/* =====================================================
   REPORT BUTTON CONTROL
===================================================== */

function enableReportButton(){

  const btn = document.getElementById("viewReportBtn");

  if(!btn) return;

  btn.classList.remove("disabled-btn");
  btn.classList.add("active-report");

}


function openReport(){

  const data = sessionStorage.getItem("multiModelResults");

  if(!data){
    alert("Run all models first!");
    return;
  }

  window.location.href = "/report";
}

/* =====================================================
   KPI UPDATE
===================================================== */

function updateKPI(id,value){

  const el = document.getElementById(id);

  el.textContent = (value*100).toFixed(1)+"%";

  el.classList.remove("pending");

}


/* =====================================================
   PIE CHART
===================================================== */

function renderPieChart(data){

  const labels = Object.keys(data);
  const values = Object.values(data);

  document.getElementById("chartPlaceholder").style.display="none";

  const canvas = document.getElementById("trafficChart");

  canvas.style.display="block";

  const ctx = canvas.getContext("2d");

  if(trafficChart) trafficChart.destroy();

  trafficChart = new Chart(ctx,{

    type:"doughnut",

    data:{
      labels:labels,
      datasets:[{
        data:values,
        backgroundColor:CHART_COLORS.slice(0,labels.length),
        borderWidth:3,
        borderColor:"#ffffff",
        hoverOffset:8
      }]
    },

    options:{

      responsive:true,
      maintainAspectRatio:false,
      cutout:"58%",

      plugins:{

        legend:{
          position:"bottom",
          labels:{
            padding:16
          }
        },

        tooltip:{
          callbacks:{
            label:(ctx)=>{

              const total = ctx.dataset.data.reduce((a,b)=>a+b,0);
              const pct = ((ctx.parsed/total)*100).toFixed(1);

              return ` ${ctx.label}: ${ctx.parsed} flows (${pct}%)`;

            }
          }
        }

      }

    }

  });

  renderBarChart(data);

}


/* =====================================================
   BAR CHART
===================================================== */

function renderBarChart(data){

  const wrap = document.getElementById("barChartWrap");

  const total = Object.values(data).reduce((a,b)=>a+b,0);

  const sorted = Object.entries(data).sort((a,b)=>b[1]-a[1]);

  let html = '<div class="bar-chart-wrap">';

  sorted.forEach(([label,val],i)=>{

    const pct = ((val/total)*100).toFixed(1);

    const color = CHART_COLORS[i%CHART_COLORS.length];

    html += `

      <div class="bar-row">

        <div class="bar-label">${label}</div>

        <div class="bar-track">
          <div class="bar-fill" style="background:${color};width:${pct}%"></div>
        </div>

        <div class="bar-pct">${pct}%</div>

      </div>

    `;

  });

  html += "</div>";

  wrap.innerHTML = html;

}




/* =====================================================
   DRAG DROP VISUAL
===================================================== */

document.addEventListener("DOMContentLoaded",()=>{

  const zone = document.getElementById("uploadZone");

  if(zone){

    zone.addEventListener("dragover",(e)=>{
      e.preventDefault();
      zone.classList.add("drag-over");
    });

    zone.addEventListener("dragleave",()=>{
      zone.classList.remove("drag-over");
    });

    zone.addEventListener("drop",(e)=>{
      e.preventDefault();
      zone.classList.remove("drag-over");
    });

  }

  // 🔥 CLEAR OLD REPORT DATA
  sessionStorage.removeItem("multiModelResults");

});