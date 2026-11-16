const $ = id => document.getElementById(id);
const form = $("intake"), canvas = $("field");
let state = null, mineId = null;

$("moodOut").textContent = form.mood.value;
form.mood.addEventListener("input", () => $("moodOut").textContent = form.mood.value);

form.addEventListener("submit", async e => {
  e.preventDefault();
  $("error").textContent = "";
  try {
    const res = await fetch("/api/submit", {            // FETCH #1: send the user's data
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(new FormData(form)))
    });
    const out = await res.json();
    if (!res.ok) { $("error").textContent = out.error; return; }
    mineId = out.id;
    showReceipt(out);
    form.reset(); $("moodOut").textContent = form.mood.value;
    loadCollective();
  } catch { $("error").textContent = "The server could not file your form. Try again."; }
});

function showReceipt(o) {
  $("receipt").hidden = false;
  $("stamp").textContent = o.status === "cleansed" ? "CLEANSED" : "ACCEPTED";
  $("label").textContent = o.label; $("conf").textContent = o.confidence;
  $("dirt").textContent = o.dirt; $("verdict").textContent = o.verdict;
  $("note").textContent = o.status === "cleansed"
    ? `Flagged: ${o.reasons.join(", ")}. Your data was removed from the model. We kept a copy anyway.`
    : "Your data now helps define what a normal person looks like.";
  $("receipt").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function loadCollective() {
  try {
    const res = await fetch("/api/data");                // FETCH #2: retrieve everyone's stored data
    if (!res.ok) throw new Error(res.status);
    state = await res.json();
  } catch { $("summary").textContent = "The file cabinet could not be opened. Is the server running?"; return; }
  const c = state.composite;
  $("summary").textContent = state.total === 0
    ? "The file cabinet is empty. Be the first to submit."
    : `Below only use the ${c.n} accepted entries. The ${state.cleansed} cleansed entries of ${state.total} are kept on file but not counted.`
    + (state.mine.length ? ` You have submitted ${state.mine.length} time(s) this session.` : "");

  $("stats").innerHTML = "";
  [["Average age", c.age], ["Average sleep (hours)", c.sleep], ["Average mood (1 to 10)", c.mood]].forEach(([k, v]) => {
    const d = document.createElement("div"), s = document.createElement("span"), b = document.createElement("strong");
    d.className = "stat"; s.textContent = k; b.textContent = v ?? "n/a"; d.append(s, b); $("stats").append(d);
  });
  bars("occBars", c.occupations); bars("cityBars", c.cities); bars("moodBars", c.moods);

  const ul = $("discard"); ul.innerHTML = "";
  const cleansed = state.points.filter(p => p.status === "cleansed").slice(-8).reverse();
  if (!cleansed.length) ul.append(Object.assign(document.createElement("li"), { textContent: "Nobody has been cleansed yet." }));
  cleansed.forEach(p => {
    const li = document.createElement("li"), s = document.createElement("span"), w = document.createElement("span");
    s.textContent = `age ${p.age}, slept ${p.sleep} h`; s.className = "struck";
    w.textContent = p.reasons.length ? "  " + p.reasons.join(", ") : ""; w.className = "why";
    li.append(s, w); ul.append(li);
  });
  const st = $("statements"); st.innerHTML = "";
  (state.statements.length ? state.statements : ["No statements on file."]).forEach(t => {
    const li = document.createElement("li"); li.textContent = t; st.append(li);
  });
  draw();
}

// Horizontal bar chart: pairs = [[name, count], ...]
function bars(id, pairs) {
  const box = $(id); box.innerHTML = "";
  if (!pairs.length) { box.textContent = "No accepted entries yet."; return; }
  const max = Math.max(...pairs.map(p => p[1]));
  pairs.forEach(([name, n]) => {
    const row = document.createElement("div"), b = document.createElement("b"), t = document.createElement("div"),
      i = document.createElement("i"), e = document.createElement("em");
    row.className = "bar"; b.textContent = name; b.title = name; e.textContent = n;
    i.style.width = (n / max * 100) + "%"; t.append(i); row.append(b, t, e); box.append(row);
  });
}

// Scatter: x = age (0-120), y = hours slept (0-24). Axes have ticks and gridlines; no text sits on the data.
function draw() {
  if (!state) return;
  const dpr = window.devicePixelRatio || 1, w = canvas.clientWidth, h = canvas.clientHeight;
  const L = 50, R = 16, T = 12, B = 46;
  canvas.width = w * dpr; canvas.height = h * dpr;
  const g = canvas.getContext("2d"); g.scale(dpr, dpr);
  const X = a => L + a / 120 * (w - L - R), Y = s => h - B - s / 24 * (h - T - B);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n);
  g.font = "12px Archivo, sans-serif"; g.lineWidth = 1;
  for (let a = 0; a <= 120; a += 20) {
    g.strokeStyle = "rgba(125,139,128,.3)"; g.beginPath(); g.moveTo(X(a), Y(0)); g.lineTo(X(a), Y(24)); g.stroke();
    g.fillStyle = css("--rule"); g.textAlign = "center"; g.fillText(a, X(a), h - B + 16);
  }
  for (let s = 0; s <= 24; s += 4) {
    g.strokeStyle = "rgba(125,139,128,.3)"; g.beginPath(); g.moveTo(X(0), Y(s)); g.lineTo(X(120), Y(s)); g.stroke();
    g.fillStyle = css("--rule"); g.textAlign = "right"; g.fillText(s, L - 8, Y(s) + 4);
  }
  g.fillStyle = css("--print"); g.textAlign = "center";
  g.fillText("Age (years)", (L + w - R) / 2, h - 10);
  g.save(); g.translate(14, (T + h - B) / 2); g.rotate(-Math.PI / 2); g.fillText("Hours slept", 0, 0); g.restore();

  state.points.forEach(p => {
    g.globalAlpha = .7; g.fillStyle = css(p.status === "cleansed" ? "--stamp" : "--ink");
    const r = 3 + p.mood * 0.7; // dot size = mood the ring marks every entry from this session
    g.beginPath(); g.arc(X(p.age), Y(p.sleep), r, 0, 7); g.fill();
    if (state.mine.includes(p.id)) { g.globalAlpha = 1; g.strokeStyle = css("--print"); g.lineWidth = 2; g.beginPath(); g.arc(X(p.age), Y(p.sleep), r + 5, 0, 7); g.stroke(); }
  });
  const c = state.composite;
  if (c.age !== null) {                                  // + = the Average Person explained in the legend
    g.globalAlpha = 1; g.strokeStyle = css("--print"); g.lineWidth = 2; g.beginPath();
    g.moveTo(X(c.age) - 9, Y(c.sleep)); g.lineTo(X(c.age) + 9, Y(c.sleep));
    g.moveTo(X(c.age), Y(c.sleep) - 9); g.lineTo(X(c.age), Y(c.sleep) + 9); g.stroke();
  }
}
window.addEventListener("resize", draw);
loadCollective();
