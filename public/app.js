const DIVISION_ORDER = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"];
const METRIC_KEYS = {
  batter: ["runs", "hr", "rbi", "sb", "avg", "obp", "slg", "wrc_plus"],
  sp: ["era", "whip", "k9", "bb9", "stuff_plus", "location_plus"],
  rp: ["era", "k9", "bb9", "k_pct", "stuff_plus"],
};

const app = document.getElementById("app");
let snapshot = null;
let injuriesSnapshot = null;
let injuryDataUnavailable = false;
let sortState = {};
let expandedRows = { sp: null, rp: null };

async function loadData() {
  const [snapshotRes, injuryRes] = await Promise.all([
    fetch("/data/latest/depth-charts.json", { cache: "no-store" }),
    fetch("/data/latest/injuries.json", { cache: "no-store" }).catch(() => null),
  ]);
  if (!snapshotRes.ok) throw new Error(`Failed to load snapshot: ${snapshotRes.status}`);
  snapshot = await snapshotRes.json();

  if (injuryRes && injuryRes.ok) {
    injuriesSnapshot = await injuryRes.json();
    injuryDataUnavailable = false;
  } else {
    injuriesSnapshot = null;
    injuryDataUnavailable = true;
  }
}

function safeMetric(value) {
  const v = String(value ?? "").trim();
  if (!v) return `<span class="missing-cell" title="No value available">--</span>`;
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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatTimestamp(value) {
  if (!value) return "--";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function findInjuryTeam(abbr) {
  return injuriesSnapshot?.teams?.find((team) => team.abbr === abbr) || null;
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

function rowIdentity(sectionId, row) {
  const explicitId = String(row.playerId ?? "").trim();
  if (explicitId) return `${sectionId}:${explicitId}`;
  const fallback = Object.prototype.hasOwnProperty.call(row, "order") ? row.order : row.role;
  return `${sectionId}:${fallback}:${row.name}`;
}

function primaryValueKey(row) {
  return Object.prototype.hasOwnProperty.call(row, "order") ? "order" : "role";
}

function renderPrimaryCell(sectionId, row, expanded) {
  const key = primaryValueKey(row);
  return `<span class="toggle-indicator" aria-hidden="true">${expanded ? "▾" : "▸"}</span>${safeMetric(row[key])}`;
}

function renderPlayerNameCell(sectionId, row) {
  const position = String(row.position ?? "").trim();
  const positionMarkup = sectionId.startsWith("batter") && position
    ? `<span class="player-position" aria-label="Position ${escapeHtml(position)}" title="Position ${escapeHtml(position)}">${escapeHtml(position)}</span>`
    : "";
  let platoonLabel = "";
  if (row.platoonRole === "vsR_only") platoonLabel = `<span class="platoon-tag" title="Published only against right-handed pitching">vs RHP only</span>`;
  if (row.platoonRole === "vsL_only") platoonLabel = `<span class="platoon-tag" title="Published only against left-handed pitching">vs LHP only</span>`;
  return `<a class="player-link" href="${row.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(row.name)}</a>${positionMarkup}${platoonLabel}`;
}

function renderHistoryCell(sectionId, row, historyRow, column) {
  const hasPrimaryLabelColumn = Object.prototype.hasOwnProperty.call(row, "order") || Object.prototype.hasOwnProperty.call(row, "role");
  if (column.key === "name") {
    return hasPrimaryLabelColumn
      ? `<span class="history-blank" aria-hidden="true"></span>`
      : `<span class="history-season">${historyRow.season}</span>`;
  }
  if (column.key === "position") {
    return `<span class="history-blank" aria-hidden="true"></span>`;
  }
  if (column.key === "order" || column.key === "role") {
    return `<span class="history-season">${historyRow.season}</span>`;
  }
  return safeMetric(historyRow[column.key]);
}

function renderTableMarkup(sectionId, rows, columns, options = {}) {
  const { tableClass = "", expandable = true } = options;
  const state = sortState[sectionId] || { key: null, dir: "desc" };
  const ordered = state.key ? sortRows(rows, sectionId, state.key, state.dir) : rows;
  const expandedRowId = expandedRows[sectionId];
  const body = [];

  for (const row of ordered) {
    const rowId = rowIdentity(sectionId, row);
    const expanded = expandable && expandedRowId === rowId;
    const hasPrimaryLabelColumn = columns.some((column) => column.key === "order" || column.key === "role");
    body.push(`
      <tr class="primary-row${expandable ? " expandable-row" : ""}${expanded ? " is-expanded" : ""}"${expandable ? ` data-expand-section="${sectionId}" data-row-id="${escapeHtml(rowId)}"` : ""}>
        ${columns.map((column) => {
          if (column.key === "name") {
            const indicator = expandable && !hasPrimaryLabelColumn
              ? `<span class="toggle-indicator" aria-hidden="true">${expanded ? "▾" : "▸"}</span>`
              : "";
            return `<td class="player-name-cell">${indicator}${renderPlayerNameCell(sectionId, row)}</td>`;
          }
          if (column.key === "order" || column.key === "role") {
            return `<td class="primary-label-cell">${renderPrimaryCell(sectionId, row, expanded)}</td>`;
          }
          return `<td>${safeMetric(row[column.key])}</td>`;
        }).join("")}
      </tr>
    `);

    if (!expanded) continue;
    for (const historyRow of row.history || []) {
      body.push(`
        <tr class="history-row" data-parent-row-id="${escapeHtml(rowId)}">
          ${columns.map((column) => `<td>${renderHistoryCell(sectionId, row, historyRow, column)}</td>`).join("")}
        </tr>
      `);
    }
  }

  return `
    <table class="${tableClass}">
      <colgroup>
        ${columns.map((column) => `<col class="col-${column.key}">`).join("")}
      </colgroup>
      <thead>
        <tr>
          ${columns.map((c) => `<th data-section="${sectionId}" data-key="${c.key}">${c.label}${state.key === c.key ? (state.dir === "asc" ? " ↑" : " ↓") : ""}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${body.join("")}
      </tbody>
    </table>
  `;
}

function renderTable(sectionId, title, rows, columns) {
  return `
    <section class="table-wrap" id="${sectionId}">
      <h2>${title}</h2>
      ${renderTableMarkup(sectionId, rows, columns)}
    </section>
  `;
}

function renderSectionContext(id, title, metaText) {
  return `
    <section class="data-context" id="${id}">
      <h2>${title}</h2>
      <p class="section-meta">${metaText}</p>
    </section>
  `;
}

function renderInjurySection(abbr) {
  const injuryTeam = findInjuryTeam(abbr);

  if (injuryDataUnavailable || !injuryTeam) {
    return `
      <section class="table-wrap injury-wrap" id="injury">
        <div class="section-header">
          <h2>Current Injury Report</h2>
        </div>
        <div class="table-state">Current injury data is temporarily unavailable.</div>
      </section>
    `;
  }

  if (!injuryTeam.injuries.length) {
    return `
      <section class="table-wrap injury-wrap" id="injury">
        <div class="section-header">
          <h2>Current Injury Report</h2>
        </div>
        <div class="table-state">No current injury entries reported by Fangraphs.</div>
      </section>
    `;
  }

  return `
    <section class="table-wrap injury-wrap" id="injury">
      <div class="section-header">
        <h2>Current Injury Report</h2>
      </div>
      <table class="injury-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Pos</th>
            <th>Status</th>
            <th>Latest Update</th>
          </tr>
        </thead>
        <tbody>
          ${injuryTeam.injuries.map((row) => `
            <tr>
              <td><a class="player-link" href="${row.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(row.name)}</a></td>
              <td>${escapeHtml(row.position)}</td>
              <td>${escapeHtml(row.status || "--")}</td>
              <td class="update-cell">${escapeHtml(row.latest_update || "--")}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>
  `;
}

function renderBatterSection(team) {
  const batter = team.batter || {};
  const lineups = batter.lineups || {};
  const alternates = batter.alternates || {};
  const starterColumns = [
    { key: "order", label: "Order" },
    { key: "name", label: "Name" },
    { key: "age", label: "Age" },
    { key: "runs", label: "R" },
    { key: "hr", label: "HR" },
    { key: "rbi", label: "RBI" },
    { key: "sb", label: "SB" },
    { key: "avg", label: "AVG" },
    { key: "obp", label: "OBP" },
    { key: "slg", label: "SLG" },
    { key: "wrc_plus", label: "wRC+" },
  ];
  const alternateColumns = starterColumns.filter((column) => column.key !== "order");

  function renderBatterColumn(viewKey, title) {
    const starterRows = lineups[viewKey] || [];
    const alternateRows = alternates[viewKey] || [];
    return `
      <div class="batter-column">
        <div class="batter-column-header">
          <h3>${title}</h3>
        </div>
        <div class="batter-group">
          <h4>Projected Starters</h4>
          ${renderTableMarkup(`batter-${viewKey}-lineup`, starterRows, starterColumns, { tableClass: "batter-subtable batter-lineup-table" })}
        </div>
        <div class="batter-group">
          <h4>Bench</h4>
          ${alternateRows.length
            ? renderTableMarkup(`batter-${viewKey}-alternates`, alternateRows, alternateColumns, { tableClass: "batter-subtable batter-alternates-table" })
            : `<div class="table-state">No bench entries published for this handedness.</div>`}
        </div>
      </div>
    `;
  }

  return `
    <section class="table-wrap" id="batter">
      <div class="section-header batter-header">
        <h2>Batter</h2>
      </div>
      <div class="batter-comparison-grid">
        ${renderBatterColumn("vsR", "vs RHP")}
        ${renderBatterColumn("vsL", "vs LHP")}
      </div>
    </section>
  `;
}

function renderTeamPage(abbr) {
  const team = snapshot.teams.find((t) => t.abbr === abbr);
  if (!team) return renderNotFound();
  app.innerHTML = `
    <section class="team-header">
      <h1><img src="${team.logoUrl}" alt="${team.abbr} logo" style="width:34px;height:34px;vertical-align:middle;margin-right:8px;"/>${team.abbr} · ${team.name}</h1>
      <div class="meta">${team.division}</div>
    </section>

    <nav class="section-nav">
      <a href="#batter">Batter</a>
      <a href="#sp">SP</a>
      <a href="#rp">RP</a>
      <a href="#injury">Injury</a>
    </nav>

    ${renderBatterSection(team)}

    ${renderTable("sp", "SP", team.sp, [
      { key: "role", label: "Role" },
      { key: "name", label: "Name" },
      { key: "age", label: "Age" },
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
      { key: "age", label: "Age" },
      { key: "era", label: "ERA" },
      { key: "k9", label: "K/9" },
      { key: "bb9", label: "BB/9" },
      { key: "k_pct", label: "K%" },
      { key: "stuff_plus", label: "stuff+" },
    ])}

    ${renderInjurySection(abbr)}
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

  document.querySelectorAll("tr[data-expand-section]").forEach((rowEl) => {
    rowEl.addEventListener("click", (event) => {
      if (event.target.closest("a.player-link")) return;
      const sectionId = rowEl.dataset.expandSection;
      const rowId = rowEl.dataset.rowId;
      if (!sectionId || !rowId) return;
      expandedRows[sectionId] = expandedRows[sectionId] === rowId ? null : rowId;
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
