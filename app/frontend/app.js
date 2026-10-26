// Harbourline Capital Deal Room — single-page frontend (no build step). Every call runs as the active Databricks role.
const $ = (s, r = document) => r.querySelector(s);
const esc = (x) => String(x ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n, d = 0) => (n === null || n === undefined || n === "" || isNaN(+n)) ? esc(n ?? "—") : (+n).toLocaleString("en-US", { maximumFractionDigits: d, minimumFractionDigits: d });
let ME = null;
const J = (x) => esc(JSON.stringify(x));   // safe value inside an onclick="…" attribute

async function api(path, opts = {}) {
  const o = { headers: {}, ...opts };
  if (o.body && !(o.body instanceof FormData)) { o.headers["Content-Type"] = "application/json"; o.body = JSON.stringify(o.body); }
  const r = await fetch(path, o);
  const t = await r.text();
  let j; try { j = JSON.parse(t); } catch { j = t; }
  if (!r.ok) { const d = j && j.detail !== undefined ? j.detail : j; throw new Error(typeof d === "string" ? d : JSON.stringify(d)); }
  return j;
}
function toast(msg, err = false) { const t = $("#toast"); t.textContent = msg; t.className = "toast" + (err ? " err" : ""); clearTimeout(t._h); t._h = setTimeout(() => t.classList.add("hidden"), 5000); }
async function act(fn, ok) { try { const r = await fn(); if (ok) toast(ok); return r; } catch (e) { toast(e.message, true); throw e; } }
function openDrawer(title, html) { $("#drawer-title").textContent = title; $("#drawer-body").innerHTML = html; $("#drawer").classList.remove("hidden"); }
function closeDrawer() { $("#drawer").classList.add("hidden"); }
const pill = (s) => { const m = { Approved: "ok", approved: "ok", synced: "ok", clean: "ok", Classified: "ok", posted: "ok", posting: "warn", Waived: "", NotApplicable: "",
  Received: "warn", Pending: "warn", flagged: "bad", Missing: "bad", rejected: "bad", "Needs review": "warn", clarification: "warn",
  submitted: "warn", "in preview": "warn", l1_approved: "warn", evaluated: "warn", draft: "", suspended: "bad", retired: "" }; return `<span class="pill ${m[s] ?? ""}">${esc(s)}</span>`; };
const conf = (c) => c === null || c === undefined ? "" : `<span class="conf ${c >= 0.8 ? "hi" : "lo"}">${(+c).toFixed(2)}</span>`;

const PAGES = {
  tasks: ["Home", "My tasks"], dealroom: ["Investments", "Deal Rooms"], stage3: ["Investments", "Stage 3 Monitoring"],
  audit: ["Governance", "Audit trail"], portal: ["External", "Solace Grid Deal Room"],
};
const ROLE_LABEL = { "role-business-user": "Fund I portfolio owner", "role-approver": "Head of Investment · IC",
  "role-it-ai-owner": "IT & AI owner", "role-external-gp": "External GP (Solace Grid)" };

async function boot() {
  try { ME = await api("/api/me"); } catch (e) { $("#page").innerHTML = `<div class="banner">${esc(e.message)}</div>`; return; }
  const chip = $("#rolechip");
  chip.textContent = ME.is_role ? `${ME.role} · ${ROLE_LABEL[ME.role] || ""}` : `${ME.email} (no role)`;
  chip.className = "chip" + (ME.is_role ? "" : " user");
  const ws = `${ME.host}/?o=${ME.workspace_id}`;
  $("#switchmenu").innerHTML = `<p><b>Two steps, same role:</b> ① switch the workspace (dashboards and Ask Genie run as the workspace identity), ② sign out of the app and sign in as that role.</p>` +
    Object.entries(ME.role_ids).map(([r, id]) => `<a href="${ws}&aid=${id}" target="hl-ws">① Workspace → ${esc(r)} <span class="small muted">${esc(ROLE_LABEL[r])}</span></a>`).join("") +
    `<a href="/.auth/sign_out"><b>② Sign out of the app → choose the same role</b></a>`;
  $("#switch").onclick = () => $("#switchmenu").classList.toggle("hidden");
  const sections = {};
  ME.pages.forEach((p) => { const [s] = PAGES[p]; (sections[s] = sections[s] || []).push(p); });
  $("#nav").innerHTML = Object.entries(sections).map(([s, ps]) => `<div class="sec">${esc(s)}</div>` +
    ps.map((p) => `<a data-p="${p}" onclick="${p === "dealroom" ? "DR_INV=null;" : ""}go('${p}')">${esc(PAGES[p][1])}</a>`).join("")).join("");
  const start = location.hash.slice(1); go(ME.pages.includes(start) ? start : ME.pages[0]);
}

function go(p) {
  location.hash = p; document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("on", a.dataset.p === p));
  $("#title").textContent = PAGES[p][1]; $("#page").innerHTML = `<p class="muted">Loading…</p>`;
  const roleNote = ME.is_role ? "" : `<div class="banner">You are signed in as yourself, not a role. Use “Switch role” to see the demo as a Harbourline persona (row-level security applies per role).</div>`;
  Promise.resolve(R[p]()).then((html) => { if (html !== undefined) $("#page").innerHTML = roleNote + html; if (p === "dealroom") drTab(); })
    .catch((e) => { $("#page").innerHTML = roleNote + `<div class="banner">${esc(e.message)}</div>`; });
}

const R = {};

// ---------------- My tasks ----------------
R.tasks = async () => {
  const t = await api("/api/tasks");
  const sev = { High: "bad", Medium: "warn", Low: "ok" };
  const rows = t.tasks.map((x) => `<tr class="click" onclick="go('${x.page}')"><td><span class="pill ${sev[x.severity] || "navy"}">${esc(x.severity || "")}</span></td>
    <td>${esc(x.title)}</td><td class="small">${esc(x.owner || "")}</td><td class="small">${esc(x.status || "")}</td>
    <td class="right small">${x.age_days == null ? "—" : esc(String(x.age_days)) + " d"}</td><td class="small">${esc(x.next_action || "")}</td>
    <td class="right"><span class="pill navy">${esc(PAGES[x.page][1])}</span></td></tr>`).join("");
  return `<div class="card"><h3>Work queue — ${esc(t.role)}</h3>${rows ? `<table><tr><th>Severity</th><th>Item</th><th>Owner</th><th>Status</th><th class="right">Age</th><th>Next action</th><th></th></tr>${rows}</table>` : `<p class="muted">Nothing waiting for you.</p>`}</div>
  <p class="muted small mt">One inbox for the active role: approvals, reviews, uploads and budgets. Data visible here is filtered by Unity Catalog for ${esc(t.role)}.</p>`;
};

// ---------------- Deal rooms ----------------
let DR = null, DR_TAB = "approvals", DR_INV = null;
const drUrl = (sfx = "") => `/api/dealroom/${encodeURIComponent(DR_INV)}${sfx}`;
const STAGE_NAME = { 1: "Stage 1 · Screening", 2: "Stage 2 · Due Diligence", 3: "Stage 3 · Post-investment" };
R.dealroom = async () => {
  if (DR_INV) { DR = await api(drUrl()); return renderDeal(); }
  const L = await api("/api/dealrooms");
  const rows = L.map((d) => `<tr class="click" onclick="${d.has_room ? `openDeal(${J(d.name)})` : "go('stage3')"}">
      <td><b>${esc(d.name)}</b><div class="small muted">${esc(d.sector)}</div></td><td>${pill(d.portfolio)}</td><td>${esc(STAGE_NAME[d.stage] || d.stage)}</td>
      <td class="right">${fmt(d.files)}</td><td>${+d.needs_review ? pill("Needs review") + ` ${d.needs_review}` : ""}</td>
      <td class="small muted">${esc(d.last_file || "—")}</td><td class="right">${d.has_room ? `<button class="sm">Open deal room →</button>` : `<span class="small muted">Stage 3 Monitoring →</span>`}</td></tr>`).join("");
  return `<div class="card"><h3>My deals</h3><p class="small muted">Deals you can see — the list is filtered by your role (Unity Catalog row filter), not by the app.</p>
    <table><tr><th>Deal</th><th>Portfolio</th><th>Stage</th><th class="right">Files</th><th>AI review</th><th>Last file</th><th></th></tr>${rows}</table></div>`;
};
function openDeal(inv) { DR_INV = inv; DR_TAB = "approvals"; go("dealroom"); }
function dealList() { DR_INV = null; go("dealroom"); }
function renderDeal() {
  const d = DR, names = STAGE_NAME;
  const steps = [1, 2, 3].map((s) => `<span class="s ${s < d.stage ? "done" : s === d.stage ? "cur" : ""}">${names[s]}</span>`).join("›");
  const cur = d.items.filter((i) => i.stage === d.stage);
  const canApprove = ME.role === "role-approver";
  const rows = cur.map((i) => {
    const f = i.file, ex = f ? d.extracts.filter((e) => e.file_id === f.file_id) : [];
    const mc = ex.length ? Math.min(...ex.map((e) => +e.confidence || 0)) : null;
    const btns = canApprove && !["Approved", "Waived", "NotApplicable"].includes(i.status) ?
      (i.kind === "approval" || f ? `<button class="sm" onclick="dealItem(${i.stage},${J(i.item)},'Approved')">Approve</button>` : "") +
      (i.requirement !== "Mandatory" ? ` <button class="sm ghost" onclick="dealItem(${i.stage},${J(i.item)},'Waived')">Waive</button>` : "") : "";
    return `<tr><td>${esc(i.item)}<div class="small muted">${esc(i.kind)}</div></td><td>${esc(i.requirement)}</td><td>${pill(i.status)}</td>
      <td>${f ? `<a href="#" onclick="fileDrawer(${J(f.file_id)});return false">${esc(f.name)}</a> ${pill(f.classification)} ${f.status === "Needs review" ? pill("Needs review") : ""}` : `<span class="muted">—</span>`}</td>
      <td>${mc !== null ? conf(mc) : ""}</td><td class="right">${btns}</td></tr>`;
  }).join("");
  const g = d.gate;
  return `<p class="small"><a href="#" onclick="dealList();return false">← My deals</a></p>
  <div class="row"><h2 style="margin:0;color:var(--navy)">${esc(d.investment)}</h2><span class="pill">Fund I</span><span class="muted">gate due ${esc(d.gate_due || "—")}</span></div>
  <div class="stepper">${steps}</div>
  <div class="grid g3"><div class="tile"><div class="k">Completion % (approved required items)</div><div class="v">${fmt(g.completion_pct, 1)}%</div></div>
    <div class="tile"><div class="k">Gaps</div><div class="v">${g.gaps.length}</div><div class="small muted">${esc(g.gaps.join(", "))}</div></div>
    <div class="tile"><div class="k">Risk alerts</div><div class="v">${d.alerts.length}</div><div class="small muted">${d.alerts.map((a) => esc(a.message)).join("<br>")}</div></div></div>
  <div class="main-rail mt"><div class="card"><div class="row" style="justify-content:space-between"><h3>Stage checklist</h3>
      <div class="row">${ME.role !== "role-external-gp" && d.stage === 2 ? `<button class="ghost sm" onclick="dropFiles()">Receive Stage 2 pack (landing zone)</button>` : ""}
      ${canApprove ? `<button class="navy" ${g.can_advance ? "" : "disabled"} title="${esc(g.can_advance ? "" : "Locked: " + [...g.gaps, ...g.missing_approvals].join(", "))}" onclick="advance()">Advance stage →</button>` : ""}</div></div>
      <table><tr><th>Item</th><th>Requirement</th><th>Status</th><th>Source file</th><th>AI conf.</th><th></th></tr>${rows}</table>
      <p class="small muted">Completion counts approved items only; waived / not-applicable leave the denominator; optional items never count. Stage approvals unlock when documents are complete.</p></div>
    <div class="card"><div class="tabs">${["approvals", "thread", "factors"].map((t) => `<a class="${DR_TAB === t ? "on" : ""}" onclick="DR_TAB='${t}';drTab()">${{ approvals: "Approvals", thread: "Thread", factors: "External factors" }[t]}</a>`).join("")}</div><div id="drtab"></div></div></div>`;
}
async function drTab() {
  document.querySelectorAll(".tabs a").forEach((a) => a.classList.toggle("on", a.textContent.toLowerCase().startsWith(DR_TAB.slice(0, 4))));
  const el = $("#drtab"); if (!el) return;
  if (DR_TAB === "approvals") {
    const ap = DR.items.filter((i) => i.kind === "approval");
    el.innerHTML = ap.map((i) => `<div class="msg">${pill(i.status)} ${esc(i.item)} <span class="m">stage ${i.stage}${i.updated ? ` · ${esc(i.updated.as)} (${esc(i.updated.by)})` : ""}</span></div>`).join("");
  } else if (DR_TAB === "thread") {
    const t = await api(`/api/threads/${encodeURIComponent(DR_INV)}`);
    el.innerHTML = `<div class="thread">${t.map((m) => `<div class="msg">${esc(m.body)}<div class="m">${esc(m.run_as)} · ${esc(m.at)}</div></div>`).join("")}</div>
      <textarea id="tmsg" rows="2" placeholder="Message the GP / team"></textarea><button class="sm mt" onclick="postThread()">Send</button>`;
  } else {
    const f = await api("/api/factors");
    const unit = { pct: "%", usd_bbl: " $/bbl", fx: "", index: "" };
    const dir = (x) => x.prev_value === null || x.prev_value === undefined || +x.value === +x.prev_value ? "flat" : +x.value > +x.prev_value ? "up" : "down";
    const chg = (x) => {
      if (dir(x) === "flat") return `<div class="fx-chg flat">unch.</div>`;
      const dl = x.value - x.prev_value, sg = dl > 0 ? "+" : "";
      return x.unit === "pct" ? `<div class="fx-chg ${dir(x)}">${sg}${Math.round(dl * 100)} bp</div>`
        : `<div class="fx-chg ${dir(x)}">${sg}${fmt(dl / x.prev_value * 100, 2)}%<div>${sg}${fmt(dl, x.unit === "fx" ? 4 : 2)}</div></div>`;
    };
    el.innerHTML = `<div class="advisory" id="fxnote"><b>AI risk note · advisory</b> — <span class="muted">reading today's factors for this deal…</span></div>
      <div class="fx-board">${f.map((x) => `<div class="fx-row ${dir(x)}">
        <div><div class="fx-name">${esc(x.label)}</div><div class="fx-sub">${esc(x.tag.replace(":", " · "))}</div></div>
        <div class="fx-last">${fmt(x.value, x.unit === "index" ? 0 : x.unit === "fx" ? 4 : 2)}${unit[x.unit] ?? ""}<div class="fx-sub">${esc(x.observed_at)}</div></div>${chg(x)}</div>`).join("")}
        <div class="fx-foot">Daily Lakeflow job · FRED, HKMA, PBOC, ECB, BoE, HSI · served from ${f.length && f[0].served_from === "lakebase" ? "Lakebase (synced table)" : "Delta"}</div></div>`;
    try {
      const n = await api(drUrl("/factor-note"));
      $("#fxnote").innerHTML = `<b>AI risk note · advisory</b> <span class="small muted">ai_query · ${esc(n.model)} · ${n.factors} factors as of ${esc(n.as_of || "—")}</span>
        <p style="margin:.4em 0 0">${esc(n.note)}</p><p class="small muted" style="margin:.3em 0 0">Context only — a factor never moves Completion % or approves a stage.</p>`;
    } catch (e) { $("#fxnote").innerHTML = `<b>AI risk note</b> — <span class="muted">unavailable: ${esc(e.message || e)}</span>`; }
  }
}
async function dealItem(stage, item, status) { DR = await act(() => api(drUrl("/item"), { method: "POST", body: { stage, item, status } }), `${item}: ${status}`); $("#page").innerHTML = renderDeal(); drTab(); }
async function advance() { DR = await act(() => api(drUrl("/advance"), { method: "POST" }), "Stage advanced"); $("#page").innerHTML = renderDeal(); drTab(); }
async function postThread() { await act(() => api(`/api/threads/${encodeURIComponent(DR_INV)}`, { method: "POST", body: { body: $("#tmsg").value } }), "Sent"); drTab(); }
async function dropFiles() { const r = await act(() => api(drUrl("/drop"), { method: "POST" })); watchJob(r.run_id, "Auto Loader ingest + AI classification", () => go("dealroom")); }
const FIELD_LABEL = { company_name: "Company", pre_money_valuation_usd_m: "Pre-money valuation (USD m)", fy2025_revenue_usd_m: "FY2025 revenue (USD m)",
  fy2025_ebitda_usd_m: "FY2025 EBITDA (USD m)", document_date: "Document date" };
function fileDrawer(fid) {
  const f = DR.files.find((x) => x.file_id === fid), ex = DR.extracts.filter((e) => e.file_id === fid);
  const act = (e) => e.reviewed_by ? `<span class="small muted">✓ ${esc(e.reviewed_by)}</span>` :
    `<button class="sm" onclick="review(${J(fid)},${J(e.field)},null)">Confirm</button> <button class="sm ghost" onclick="correct(${J(fid)},${J(e.field)})">Correct</button>`;
  const val = (e) => `${esc(e.corrected_value || e.value)}${e.corrected_value ? ` <span class="small muted">(AI said ${esc(e.value)})</span>` : ""}`;
  const t = ex.find((e) => e.field === "ai_document_type"), c = ex.find((e) => e.field === "ai_classification");
  const routed = (t && c) ? (Math.min(+t.confidence, +c.confidence) >= 0.8
      ? `<span class="pill ok">auto-filed</span> both scores ≥ 0.80 → filed to checklist item <b>${esc(t.value)}</b>, labelled <b>${esc(f.classification)}</b>`
      : `<span class="pill warn">sent to review</span> a score is below 0.80 → a person confirms; label kept restrictive (<b>${esc(f.classification)}</b>)`) : "";
  const clsRows = [["Document type → checklist item", t], ["Information classification (4-level standard)", c]].filter(([, e]) => e)
    .map(([lbl, e]) => `<tr><td>${lbl}</td><td><b>${val(e)}</b></td><td>${conf(e.confidence)}</td><td>${act(e)}</td></tr>`).join("");
  const exRows = ex.filter((e) => !e.field.startsWith("ai_")).map((e) => `<tr><td>${esc(FIELD_LABEL[e.field] || e.field)}</td><td><b>${val(e)}</b></td><td>${conf(e.confidence)}</td><td>${act(e)}</td></tr>`).join("");
  openDrawer(f.name, `<div class="row">${pill(f.file_type)} ${pill(f.classification)} ${pill(f.status)} <span class="small muted">${esc(f.source)} · ${esc(f.received_at)}</span></div>
    <div class="advisory"><b>What the AI did · advisory</b> — <code>ai_parse_document</code> read the file → <code>ai_classify</code> filed and labelled it → <code>ai_extract</code> pulled the key fields, each with a confidence score. You confirm or correct; every decision is audited.</div>
    <h4>1 · ai_classify</h4>${clsRows ? `<table><tr><th>Decision</th><th>AI result</th><th>Conf.</th><th></th></tr>${clsRows}</table><p class="small">${routed}</p>` : `<p class="muted">Not classified yet.</p>`}
    <h4>2 · ai_extract</h4>${exRows ? `<table><tr><th>Field</th><th>Value</th><th>Conf.</th><th></th></tr>${exRows}</table>` : `<p class="muted">No key figures in this document.</p>`}
    <h4>Source document</h4><iframe class="embed" style="height:50vh" src="/api/files/${encodeURIComponent(fid)}"></iframe>`);
}
async function review(fid, field, val) { await act(() => api(`/api/extract/${fid}/review`, { method: "POST", body: { field, corrected_value: val } }), "Recorded"); DR = await api(drUrl()); fileDrawer(fid); }
function correct(fid, field) { const v = prompt(`Correct value for ${field}`); if (v) review(fid, field, v); }
async function watchJob(run, label, done) {
  toast(`${label}: job run ${run} started…`);
  for (let i = 0; i < 120; i++) { await new Promise((r) => setTimeout(r, 5000)); const s = await api(`/api/jobs/${run}`);
    if (s.state.includes("TERMINATED") || s.state.includes("INTERNAL_ERROR") || s.state.includes("SKIPPED")) { toast(`${label}: ${s.result}`, !s.result.includes("SUCCESS")); if (done) done(); return s; } }
}

// ---------------- Stage 3 ----------------
R.stage3 = async () => {
  const s = await api("/api/stage3");
  const props = s.proposals.map((p) => { const r = p.result || {}; return `<div class="msg">${pill(p.status)} ${esc(p.request)}
    <div class="m">${esc(p.run_as)} · ${r.spec ? esc(r.spec.metric + " · " + r.spec.visual) : esc((r.errors || []).join("; ") || r.reason || "")}</div>
    ${p.status === "proposed" ? `<button class="sm" onclick="acceptW(${p.id})">Accept into preview</button>` : ""}</div>`; }).join("");
  return `<div class="main-rail"><div><iframe class="embed" style="height:1100px" src="${s.dashboard_embed}"></iframe></div>
  <div><div class="card"><h3>Propose widget · Widget Builder agent</h3>
    <p class="small muted">AI agent on an open-weight model. It sees only the metrics your role can see.</p>
    <textarea id="wreq" rows="3">Show gross MOIC by period as a bar chart</textarea><button class="mt" onclick="proposeW()">Propose</button>
    <div id="wout" class="mt"></div></div>
    <div class="card mt"><h3>Recent proposals</h3>${props || `<p class="muted small">None yet.</p>`}</div>
    <div class="card mt"><h3>Preview → approval</h3><p class="small muted">Accepted widgets go to a <b>preview dashboard</b> (live data, each viewer's own access). After the approver approves, they're added to the official <b>Stage 3 Monitoring</b> dashboard on this page. Feedback creates a controller instruction.</p>
      <div class="row"><button class="ghost" onclick="viewExec()">Open preview</button>${ME.role === "role-approver" ? `<button class="navy" onclick="publishExec()">Approve → publish to Stage 3 Monitoring</button>` : `<span class="small muted">Approval: Head of Investment</span>`}</div>
      <textarea id="fb" rows="2" class="mt" placeholder="Feedback to the controller…"></textarea><button class="sm mt" onclick="sendFb()">Send feedback</button></div>
    <p class="small muted mt">Ask questions in EN / 繁 / 简 with <b>Ask Genie</b> on the dashboard.</p></div></div>`;
};
async function proposeW() {
  $("#wout").innerHTML = `<p class="muted small">Asking the Widget Builder…</p>`;
  try { const r = await api("/api/stage3/propose", { method: "POST", body: { request: $("#wreq").value } });
    $("#wout").innerHTML = r.status === "ok" ? `<div class="advisory"><b>Proposed widget · advisory</b><table>
      ${["title", "metric", "source", "formula", "grain", "visual"].map((k) => `<tr><td class="muted">${k}</td><td>${esc(r.spec[k])}</td></tr>`).join("")}
      <tr><td class="muted">sources</td><td>${esc(r.spec.sources.join(", "))}</td></tr><tr><td class="muted">prompt</td><td class="small">${esc(r.prompt_uri)}</td></tr></table>
      ${previewW(r.spec, r.preview)}
      <button class="sm" onclick="acceptW(${r.id})">Accept into preview</button></div>`
      : `<div class="banner">${esc(r.status)}: ${esc((r.errors || []).join("; ") || r.reason)}</div>`;
  } catch (e) { $("#wout").innerHTML = `<div class="banner">${esc(e.message)}</div>`; }
}
function previewW(spec, rows) {
  const head = `<div class="small muted mt"><b>Preview</b> — live data, as your role (the same query the widget will run)</div>`;
  if (!rows || rows.error) return head + `<p class="small muted">${esc(rows && rows.error || "no preview")}</p>`;
  if (!rows.length) return head + `<p class="small muted">No rows visible to your role.</p>`;
  const g = spec.grain, nf = (v) => fmt(v, Math.abs(+v) < 100 ? 2 : 0);
  if (spec.visual === "counter" || !g) return head + `<div class="pv-counter">${nf(rows[0].value)}<div class="small muted">${esc(spec.metric)}</div></div>`;
  if (spec.visual === "table") return head + `<table>${rows.map((x) => `<tr><td>${esc(x[g])}</td><td class="right">${nf(x.value)}</td></tr>`).join("")}</table>`;
  const max = Math.max(...rows.map((x) => Math.abs(+x.value) || 0)) || 1;
  return head + `<div class="pv-bars">${rows.map((x) => `<div class="pv-row"><span class="pv-l">${esc(x[g])}</span>
    <span class="pv-b"><i style="width:${Math.max(2, Math.abs(+x.value) / max * 100)}%"></i></span><span class="pv-v">${nf(x.value)}</span></div>`).join("")}</div>`;
}
async function acceptW(id) { const r = await act(() => api(`/api/stage3/accept/${id}`, { method: "POST" }), "Added to the preview — awaiting approval"); go("stage3"); openDrawer("Preview — pending approval", `<iframe class="embed" style="height:85vh" src="${r.embed}"></iframe>`); }
async function publishExec() { await act(() => api("/api/stage3/publish", { method: "POST" }), "Approved — published to Stage 3 Monitoring"); go("stage3"); }
async function viewExec() { const r = await api("/api/stage3/executive"); openDrawer("Preview — pending approval", `<iframe class="embed" style="height:85vh" src="${r.embed}"></iframe>`); }
async function sendFb() { await act(() => api("/api/feedback", { method: "POST", body: { body: $("#fb").value } }), "Instruction sent to the controller"); }

// ---------------- Audit ----------------
R.audit = async () => {
  const a = await api("/api/audit");
  const rows = a.approvals.map((x) => `<tr><td class="small">${esc(x.at)}</td><td>${esc(x.scope)}</td><td>${esc(x.ref)}</td><td>${esc(x.decision)}</td><td class="small">${esc(x.note)}</td><td>${esc(x.run_as)}</td><td class="small muted">${esc(x.run_by)}</td></tr>`).join("");
  const u = (a.usage || []).map((x) => `<tr><td>${esc(x.day)}</td><td>${esc(x.agent)}</td><td>${esc(x.role)}</td><td>${esc(x.portfolio)}</td><td>${esc(x.destination_model)}</td><td class="right">${fmt(x.requests)}</td><td class="right">${fmt(x.tokens)}</td></tr>`).join("");
  return `<div class="card"><h3>Approvals &amp; actions (run as = role, run by = person)</h3><table><tr><th>When</th><th>Scope</th><th>Ref</th><th>Decision</th><th>Note</th><th>Run as</th><th>Run by</th></tr>${rows}</table></div>
  ${a.usage ? `<div class="card mt"><h3>AI calls by agent / role / portfolio (Unity Gateway)</h3><table><tr><th>Day</th><th>Agent</th><th>Role</th><th>Scope</th><th>Model</th><th class="right">Requests</th><th class="right">Tokens</th></tr>${u}</table></div>` : ""}
  <p class="small muted mt">Also in Databricks: system.access.audit (run_by / run_as), MLflow traces, deployment-job activity log, Unity Catalog lineage.</p>`;
};

// ---------------- External portal (GP) ----------------
R.portal = async () => {
  const p = await api("/api/portal");
  const files = p.files.map((f) => `<tr><td>${esc(f.name)}</td><td>${pill(f.classification)}</td><td>${pill(f.status)}</td><td class="small muted">${esc(f.uploaded_by || "Harbourline")}</td></tr>`).join("");
  const t = await api("/api/threads/Solace%20Grid%20Energy");
  return `<div class="banner">External party view — you see only the Solace Grid Energy room; Confidential Harbourline documents stay hidden except your own uploads (Unity Catalog row filter).</div>
  <div class="grid g2"><div class="card"><h3>Documents visible to you</h3>${files ? `<table><tr><th>File</th><th>Class</th><th>Status</th><th>Uploaded by</th></tr>${files}</table>` : `<p class="muted">No documents visible yet.</p>`}
    <div class="row mt"><button onclick="gpStage()">Upload Stage 2 pack (Valuation &amp; IC memos)</button><input type="file" id="up" style="width:auto"><button class="ghost" onclick="gpUpload()">Upload file</button></div></div>
  <div class="card"><h3>Thread with Harbourline Capital</h3><div class="thread">${t.map((m) => `<div class="msg">${esc(m.body)}<div class="m">${esc(m.run_as)} · ${esc(m.at)}</div></div>`).join("")}</div>
    <textarea id="tmsg" rows="2"></textarea><button class="sm mt" onclick="gpMsg()">Reply</button></div></div>`;
};
async function gpStage() { const r = await act(() => api("/api/portal/stage-gp-files", { method: "POST" }), "Uploaded"); watchJob(r.ingest_run, "Ingest", async () => { await api("/api/portal/refresh", { method: "POST" }); go("portal"); }); }
async function gpUpload() { const f = $("#up").files[0]; if (!f) return; const fd = new FormData(); fd.append("file", f); const r = await act(() => api("/api/portal/upload", { method: "POST", body: fd }), "Uploaded"); watchJob(r.ingest_run, "Ingest", async () => { await api("/api/portal/refresh", { method: "POST" }); go("portal"); }); }
async function gpMsg() { await act(() => api("/api/threads/Solace%20Grid%20Energy", { method: "POST", body: { body: $("#tmsg").value } }), "Sent"); go("portal"); }

window.addEventListener("hashchange", () => { const p = location.hash.slice(1); if (ME && ME.pages.includes(p) && !$(`nav a.on[data-p="${p}"]`)) go(p); });
boot();
