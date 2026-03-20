const DIVISION_ORDER = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"];
const METRIC_KEYS = {
  batter: ["wrc_plus", "avg", "obp", "slg"],
  sp: ["k9", "bb9", "stuff_plus", "location_plus"],
  rp: ["era", "k9", "bb9", "k_pct", "stuff_plus"],
};

const app = document.getElementById("app");
let snapshot = null;
let sortState = {};

async function loadData() {
  const res = await fetch("/data/latest/depth-charts.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load snapshot: ${res.status}`);
  snapshot = await res.json();
}

function snapshotSummary(meta) {
  return `
    <section class="status-bar">
      <div><strong>Season:</strong> ${meta.season}</div>
      <div><strong>Source:</strong> Fangraphs depth charts snapshot</div>
    </section>
  `;
}

function setUrl(path, params = null) {
  const q = params && [...params.keys()].length ? `?${params.toString()}` : "";
  history.pushState({}, "", `${path}${q}${location.hash}`);
}

function safeMetric(value) {
  const v = String(value ?? "").trim();
  if (!v) return `<span class="missing-cell" title="No 2025 value">--</span>`;
  return v;
}

function rowMissing(row, section) {
  return METRIC_KEYS[section].every((k) => !String(row[k] ?? "").trim());
}

function sortRows(rows, section, key, dir) {
  const mapped = [...rows];
  mapped.sort((a, b) => {
    const av = String(a[key] ?? "").replace("%", "").trim();
    const bv = String(b[key] ?? "").replace("%", "").trim();
    if (!av && !bv) return 0;
    if (!av) return 1;
    if (!bv) return -1;
    const an = Number(av);
    const bn = Number(bv);
    if (!Number.isNaN(an) && !Number.isNaN(bn)) return dir === "asc" ? an - bn : bn - an;
    return dir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
  });
  return mapped;
}

function parseRoute() {
  const p = location.pathname.replace(/\/+$/, "") || "/";
  if (p === "/" || p === "/teams") return { page: "teams" };
  if (p === "/about-data") return { page: "about" };
  const m = p.match(/^\/team\/([A-Za-z]{3})$/);
  if (m) return { page: "team", abbr: m[1].toUpperCase() };
  return { page: "notfound" };
}

function renderTeamsPage() {
  const params = new URLSearchParams(location.search);
  const season = Number(params.get("season") || snapshot.meta.season);
  const division = params.get("division") || "all";
  const q = (params.get("q") || "").toLowerCase();

  let teams = snapshot.teams.filter((t) => String(season) === String(snapshot.meta.season));
  if (division !== "all") teams = teams.filter((t) => t.division === division);
  if (q) {
    teams = teams.filter((t) => {
      if (t.abbr.toLowerCase().includes(q) || t.name.toLowerCase().includes(q)) return true;
      const pool = [...t.batter, ...t.sp, ...t.rp].map((r) => String(r.name || "").toLowerCase());
      return pool.some((name) => name.includes(q));
    });
  }

  const grouped = Object.fromEntries(DIVISION_ORDER.map((d) => [d, []]));
  for (const t of teams) grouped[t.division].push(t);

  app.innerHTML = `
    ${snapshotSummary(snapshot.meta)}
    <section class="filters">
      <select id="seasonSel"><option value="${snapshot.meta.season}">${snapshot.meta.season}</option></select>
      <select id="divisionSel">
        <option value="all">All Divisions</option>
        ${DIVISION_ORDER.map((d) => `<option value="${d}" ${d === division ? "selected" : ""}>${d}</option>`).join("")}
      </select>
      <input id="qInput" placeholder="Search teams or players" value="${params.get("q") || ""}">
    </section>
    <section class="division-grid">
      ${DIVISION_ORDER.map((d) => `
        <div class="division">
          <h3>${d}</h3>
          ${grouped[d].length ? grouped[d].map((t) => `
            <a class="team-card" href="/team/${t.abbr}?season=${snapshot.meta.season}" data-link>
              <div class="team-id">
                <img src="${t.logoUrl}" alt="${t.abbr} logo" />
                <div>
                  <div><strong>${t.abbr}</strong> ${t.name}</div>
                  <div class="meta">${t.batter.length} batters · ${t.sp.length} SP · ${t.rp.length} RP</div>
                </div>
              </div>
            </a>
          `).join("") : `<div class="meta">No teams match filters</div>`}
        </div>
      `).join("")}
    </section>
  `;

  function updateQuery() {
    const next = new URLSearchParams();
    next.set("season", document.getElementById("seasonSel").value);
    const d = document.getElementById("divisionSel").value;
    const qq = document.getElementById("qInput").value.trim();
    if (d !== "all") next.set("division", d);
    if (qq) next.set("q", qq);
    history.replaceState({}, "", `/teams?${next.toString()}`);
    renderTeamsPage();
  }

  ["seasonSel", "divisionSel"].forEach((id) => {
    document.getElementById(id).addEventListener("change", updateQuery);
  });
  document.getElementById("qInput").addEventListener("input", updateQuery);
}

function renderTable(sectionId, title, rows, columns) {
  const state = sortState[sectionId] || { key: null, dir: "desc" };
  const ordered = state.key ? sortRows(rows, sectionId, state.key, state.dir) : rows;

  return `
    <section class="table-wrap" id="${sectionId}">
      <h2>${title}</h2>
      <table>
        <thead>
          <tr>
            ${columns.map((c) => `<th data-section="${sectionId}" data-key="${c.key}">${c.label}${state.key === c.key ? (state.dir === "asc" ? " ↑" : " ↓") : ""}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${ordered.map((r) => {
            const rowCls = rowMissing(r, sectionId) ? "missing" : "";
            return `<tr class="${rowCls}">${columns.map((c) => {
              if (c.key === "name") return `<td><a class="ext" href="${r.url}" target="_blank" rel="noopener noreferrer">${r.name}</a></td>`;
              return `<td>${safeMetric(r[c.key])}</td>`;
            }).join("")}</tr>`;
          }).join("")}
        </tbody>
      </table>
    </section>
  `;
}

function renderTeamPage(abbr) {
  const team = snapshot.teams.find((t) => t.abbr === abbr);
  if (!team) return renderNotFound();

  app.innerHTML = `
    ${snapshotSummary(snapshot.meta)}
    <section class="team-header">
      <h1><img src="${team.logoUrl}" alt="${team.abbr} logo" style="width:34px;height:34px;vertical-align:middle;margin-right:8px;"/>${team.abbr} · ${team.name}</h1>
      <div class="meta">${team.division}</div>
    </section>

    <nav class="section-nav">
      <a href="#batter">Batter</a>
      <a href="#sp">SP</a>
      <a href="#rp">RP</a>
    </nav>

    ${renderTable("batter", "Batter", team.batter, [
      { key: "order", label: "Order" },
      { key: "name", label: "Name" },
      { key: "position", label: "Position" },
      { key: "wrc_plus", label: "wRC+" },
      { key: "avg", label: "AVG" },
      { key: "obp", label: "OBP" },
      { key: "slg", label: "SLG" },
    ])}

    ${renderTable("sp", "SP", team.sp, [
      { key: "role", label: "role" },
      { key: "name", label: "Name" },
      { key: "k9", label: "k/9" },
      { key: "bb9", label: "bb/9" },
      { key: "stuff_plus", label: "stuff+" },
      { key: "location_plus", label: "location+" },
    ])}

    ${renderTable("rp", "RP", team.rp, [
      { key: "role", label: "Role" },
      { key: "name", label: "Name" },
      { key: "era", label: "ERA" },
      { key: "k9", label: "K/9" },
      { key: "bb9", label: "BB/9" },
      { key: "k_pct", label: "K%" },
      { key: "stuff_plus", label: "stuff+" },
    ])}
  `;

  document.querySelectorAll("th[data-section]").forEach((th) => {
    th.addEventListener("click", () => {
      const sec = th.dataset.section;
      const key = th.dataset.key;
      const curr = sortState[sec] || { key: null, dir: "desc" };
      sortState[sec] = curr.key === key ? { key, dir: curr.dir === "desc" ? "asc" : "desc" } : { key, dir: "desc" };
      renderTeamPage(abbr);
    });
  });
}

function renderAbout() {
  app.innerHTML = `
    ${snapshotSummary(snapshot.meta)}
    <section class="about">
      <h1>About Data</h1>
      <p><strong>Source:</strong> Fangraphs roster resource and leaders API.</p>
      <p><strong>Matching strategy:</strong> exact name -> playerid -> normalized name.</p>
      <p><strong>Quality rules:</strong> section minimums, row-level missing metrics, warning aggregation.</p>
      <p><strong>Schema version:</strong> ${snapshot.meta.schemaVersion}</p>
    </section>
  `;
}

function renderNotFound() {
  app.innerHTML = `<section class="about"><h1>Not Found</h1><p>Unknown route. Go back to <a href="/teams" data-link>Teams</a>.</p></section>`;
}

function attachRouterHandlers() {
  document.querySelectorAll("a[data-link]").forEach((a) => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href");
      if (!href || href.startsWith("http")) return;
      e.preventDefault();
      history.pushState({}, "", href);
      render();
    });
  });
}

function render() {
  const route = parseRoute();
  if (route.page === "teams") renderTeamsPage();
  else if (route.page === "team") renderTeamPage(route.abbr);
  else if (route.page === "about") renderAbout();
  else renderNotFound();
  attachRouterHandlers();
}

window.addEventListener("popstate", render);

loadData()
  .then(() => render())
  .catch((err) => {
    app.innerHTML = `<section class="about"><h1>Unable to load data snapshot</h1><p>${err.message}</p></section>`;
  });
