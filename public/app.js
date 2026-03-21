const DIVISION_ORDER = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"];
const METRIC_KEYS = {
  batter: ["wrc_plus", "avg", "obp", "slg"],
  sp: ["era", "whip", "k9", "bb9", "stuff_plus", "location_plus"],
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

function safeMetric(value) {
  const v = String(value ?? "").trim();
  if (!v) return `<span class="missing-cell" title="No 2025 value">--</span>`;
  return v;
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
  const m = p.match(/^\/team\/([A-Za-z]{3})$/);
  if (m) return { page: "team", abbr: m[1].toUpperCase() };
  return { page: "notfound" };
}

function renderTeamsPage() {
  const grouped = Object.fromEntries(DIVISION_ORDER.map((d) => [d, []]));
  for (const t of snapshot.teams) grouped[t.division].push(t);

  app.innerHTML = `
    <section class="page-intro">
      <p class="eyebrow">Approved MLB Depth Charts</p>
      <h1>Teams</h1>
      <p class="lede">Browse the current depth chart for every club, grouped by division.</p>
    </section>
    <section class="division-grid">
      ${DIVISION_ORDER.map((d) => `
        <div class="division">
          <h3>${d}</h3>
          ${grouped[d].length ? grouped[d].map((t) => `
            <a class="team-card" href="/team/${t.abbr}" data-link>
              <div class="team-id">
                <img src="${t.logoUrl}" alt="${t.abbr} logo" />
                <div>
                  <div><strong>${t.abbr}</strong> ${t.name}</div>
                </div>
              </div>
            </a>
          `).join("") : `<div class="meta">No teams available</div>`}
        </div>
      `).join("")}
    </section>
  `;
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
            return `<tr>${columns.map((c) => {
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
  const updated = snapshot.meta.generatedAt ? new Date(snapshot.meta.generatedAt).toLocaleString() : "--";

  app.innerHTML = `
    <section class="team-header">
      <h1><img src="${team.logoUrl}" alt="${team.abbr} logo" style="width:34px;height:34px;vertical-align:middle;margin-right:8px;"/>${team.abbr} · ${team.name}</h1>
      <div class="meta">${team.division}</div>
      <p class="updated-note">Updated ${updated}</p>
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
      { key: "role", label: "Role" },
      { key: "name", label: "Name" },
      { key: "era", label: "ERA" },
      { key: "whip", label: "WHIP" },
      { key: "k9", label: "K/9" },
      { key: "bb9", label: "BB/9" },
      { key: "stuff_plus", label: "Stuff+" },
      { key: "location_plus", label: "Location+" },
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
  else renderNotFound();
  attachRouterHandlers();
}

window.addEventListener("popstate", render);

loadData()
  .then(() => render())
  .catch((err) => {
    app.innerHTML = `<section class="about"><h1>Unable to load data snapshot</h1><p>${err.message}</p></section>`;
  });
