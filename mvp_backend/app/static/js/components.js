(function (global) {
  const t = (k, f) => global.BaklavaI18n.t(k, f);

  function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function fmtNum(value, digits) {
    const n = Number(value);
    if (!isFinite(n)) return "—";
    return n.toLocaleString(global.BaklavaI18n.getLang() === "ar" ? "ar" : "en", {
      maximumFractionDigits: digits === undefined ? 3 : digits,
    });
  }

  function fmtMoney(value) {
    const n = Number(value);
    if (!isFinite(n)) return "—";
    return n.toLocaleString(global.BaklavaI18n.getLang() === "ar" ? "ar" : "en", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function fmtDate(value) {
    if (!value) return "—";
    const d = new Date(value);
    if (isNaN(d.getTime())) return escapeHtml(value);
    return d.toLocaleString(global.BaklavaI18n.getLang() === "ar" ? "ar" : "en", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }

  function toast(el, msg, ok) {
    if (!el) return;
    el.textContent = msg;
    el.className = "toast " + (ok ? "ok" : "err");
  }

  // Populate a <select> with items. opts: { value, label, placeholder, selected }
  function fillSelect(selectEl, items, opts) {
    if (!selectEl) return;
    const o = opts || {};
    const valueKey = o.value || "id";
    const labelFn =
      typeof o.label === "function"
        ? o.label
        : (item) => item[o.label || "name"];
    const placeholder = o.placeholder !== undefined ? o.placeholder : t("common.select");
    const prev = o.selected !== undefined ? String(o.selected) : selectEl.value;

    const options = [`<option value="">${escapeHtml(placeholder)}</option>`].concat(
      items.map(
        (item) =>
          `<option value="${escapeHtml(item[valueKey])}">${escapeHtml(labelFn(item))}</option>`
      )
    );
    selectEl.innerHTML = options.join("");
    if (prev && items.some((i) => String(i[valueKey]) === prev)) {
      selectEl.value = prev;
    }
  }

  async function loadProducts(category) {
    const path = category ? `/products?category=${encodeURIComponent(category)}` : "/products";
    return global.BaklavaApi.get(path);
  }

  async function populateProductSelect(selectEl, opts) {
    const o = opts || {};
    const products = await loadProducts(o.category);
    fillSelect(selectEl, products, {
      value: "id",
      label: (p) => `${p.name} (${p.code})`,
      selected: o.selected,
    });
    return products;
  }

  async function populateSupplierSelect(selectEl, opts) {
    const o = opts || {};
    const rows = await global.BaklavaApi.get("/suppliers/list");
    fillSelect(selectEl, rows, { value: "id", label: "name", selected: o.selected });
    return rows;
  }

  async function populateStoreSelect(selectEl, opts) {
    const o = opts || {};
    const rows = await global.BaklavaApi.get("/stores/list");
    fillSelect(selectEl, rows, { value: "id", label: "name", selected: o.selected });
    return rows;
  }

  // Friendly result renderer: shows labelled key/value pairs instead of raw JSON.
  // rows: array of { label, value }
  function renderResult(el, rows) {
    if (!el) return;
    const body = rows
      .filter((r) => r.value !== undefined && r.value !== null && r.value !== "")
      .map(
        (r) =>
          `<div class="result-row"><span class="result-key">${escapeHtml(r.label)}</span>` +
          `<span class="result-val">${escapeHtml(r.value)}</span></div>`
      )
      .join("");
    el.innerHTML = body;
    el.classList.add("visible");
  }

  function clearResult(el) {
    if (!el) return;
    el.innerHTML = "";
    el.classList.remove("visible");
  }

  // Render KPI cards into a container. cards: [{ label, value, tone }]
  function renderKpis(container, cards) {
    if (!container) return;
    container.innerHTML = cards
      .map(
        (c) =>
          `<div class="kpi-card ${c.tone ? "kpi-" + c.tone : ""}">
             <div class="kpi-value">${escapeHtml(c.value)}</div>
             <div class="kpi-label">${escapeHtml(c.label)}</div>
           </div>`
      )
      .join("");
  }

  // Render a table body. columns: [{ render(row) }] ; rows: array
  function renderRows(tbody, rows, columns, emptyMsg, colspan) {
    if (!tbody) return;
    if (!rows || !rows.length) {
      tbody.innerHTML = `<tr><td colspan="${colspan || columns.length}" class="empty">${escapeHtml(
        emptyMsg
      )}</td></tr>`;
      return;
    }
    tbody.innerHTML = rows
      .map(
        (row) =>
          "<tr>" +
          columns.map((col) => `<td>${col.render ? col.render(row) : escapeHtml(row[col.key])}</td>`).join("") +
          "</tr>"
      )
      .join("");
  }

  function statusBadge(status) {
    const cls =
      status === "approved" || status === "received"
        ? "ok"
        : status === "rejected"
          ? "err"
          : "warn";
    return `<span class="badge badge-${cls}">${escapeHtml(status)}</span>`;
  }

  global.BaklavaComponents = {
    escapeHtml,
    fmtNum,
    fmtMoney,
    fmtDate,
    toast,
    fillSelect,
    loadProducts,
    populateProductSelect,
    populateSupplierSelect,
    populateStoreSelect,
    renderResult,
    clearResult,
    renderKpis,
    renderRows,
    statusBadge,
  };
})(window);
