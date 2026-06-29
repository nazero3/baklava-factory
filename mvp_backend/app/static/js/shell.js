(function (global) {
  const t = (k) => global.BaklavaI18n.t(k);

  // Each item: page key, href, i18n label key, and roles allowed to see it.
  // An empty roles array means "all authenticated users".
  const NAV_GROUPS = [
    {
      labelKey: "nav.group.main",
      items: [
        { page: "dashboard", href: "/dashboard", labelKey: "nav.dashboard", roles: [] },
      ],
    },
    {
      labelKey: "nav.group.operate",
      items: [
        { page: "receiving", href: "/receiving", labelKey: "nav.receiving", roles: ["admin", "factory_manager", "warehouse"] },
        { page: "production", href: "/production", labelKey: "nav.production", roles: ["admin", "factory_manager", "production_supervisor"] },
        { page: "dispatch", href: "/dispatch", labelKey: "nav.dispatch", roles: ["admin", "factory_manager", "warehouse", "store_manager"] },
        { page: "store-return", href: "/store-return", labelKey: "nav.store_movements", roles: ["admin", "factory_manager", "store_manager"] },
      ],
    },
    {
      labelKey: "nav.group.catalog",
      items: [
        { page: "suppliers", href: "/suppliers", labelKey: "nav.suppliers", roles: ["admin", "factory_manager", "warehouse"] },
        { page: "stores", href: "/stores", labelKey: "nav.stores", roles: ["admin", "factory_manager"] },
        { page: "products", href: "/products-view", labelKey: "nav.products", roles: ["admin", "factory_manager", "accountant"] },
        { page: "recipes", href: "/recipes-view", labelKey: "nav.recipes", roles: ["admin", "factory_manager", "production_supervisor"] },
      ],
    },
    {
      labelKey: "nav.group.insights",
      items: [
        { page: "inventory", href: "/inventory-view", labelKey: "nav.inventory", roles: ["admin", "factory_manager", "accountant", "executive", "warehouse", "production_supervisor"] },
        { page: "approvals", href: "/approvals", labelKey: "nav.approvals", roles: ["admin", "factory_manager"] },
        { page: "reports", href: "/reports", labelKey: "nav.reports", roles: ["admin", "factory_manager", "accountant", "executive", "production_supervisor"] },
      ],
    },
    {
      labelKey: "nav.group.admin",
      items: [
        { page: "users", href: "/users", labelKey: "nav.users", roles: ["admin"] },
      ],
    },
  ];

  function allowed(item, role) {
    return !item.roles.length || item.roles.includes(role);
  }

  function renderNav(activePage) {
    const mount = document.getElementById("app-nav");
    if (!mount) return;

    const username = global.BaklavaAuth.getUsername();
    const role = global.BaklavaAuth.getRole();
    const roleLabel = role ? t("role." + role) : "";

    const groupsHtml = NAV_GROUPS.map((group) => {
      const visible = group.items.filter((item) => allowed(item, role));
      if (!visible.length) return "";

      // Single-item groups (e.g. Dashboard) render as a plain top-level tab.
      if (visible.length === 1) {
        const item = visible[0];
        return `<a class="tab${item.page === activePage ? " active" : ""}" href="${item.href}">${t(item.labelKey)}</a>`;
      }

      // Multi-item groups render as a hover dropdown menu.
      const activeInGroup = visible.some((item) => item.page === activePage);
      const items = visible
        .map(
          (item) =>
            `<a class="nav-dropdown-item${item.page === activePage ? " active" : ""}" href="${item.href}">${t(item.labelKey)}</a>`
        )
        .join("");
      return `<div class="nav-menu">
        <button type="button" class="nav-menu-trigger${activeInGroup ? " active" : ""}" aria-haspopup="true">
          ${t(group.labelKey)}<span class="caret" aria-hidden="true">▾</span>
        </button>
        <div class="nav-dropdown" role="menu">${items}</div>
      </div>`;
    }).join("");

    const initials = (username || "?").trim().charAt(0).toUpperCase();

    mount.innerHTML = `
      <div class="nav-top">
        <a class="logo" href="/dashboard">
          <span class="logo-mark">B</span>
          <span class="logo-text">${t("app.name")}</span>
        </a>
        <div class="user-area">
          <button type="button" class="lang-btn" id="lang-btn" title="Language">${t("common.lang_toggle")}</button>
          <span class="user-chip" title="${global.BaklavaComponents.escapeHtml(username)}">
            <span class="user-avatar">${global.BaklavaComponents.escapeHtml(initials)}</span>
            <span class="user-meta">
              <span class="user-name">${global.BaklavaComponents.escapeHtml(username)}</span>
              ${roleLabel ? `<span class="user-role">${global.BaklavaComponents.escapeHtml(roleLabel)}</span>` : ""}
            </span>
          </span>
          <button type="button" class="logout-btn" id="logout-btn">${t("common.logout")}</button>
        </div>
      </div>
      <nav class="nav-tabs-row" aria-label="Primary">${groupsHtml}</nav>
    `;

    document.getElementById("lang-btn").addEventListener("click", () => {
      global.BaklavaI18n.toggleLang();
    });

    document.getElementById("logout-btn").addEventListener("click", async () => {
      await global.BaklavaAuth.logout();
      window.location.href = "/login";
    });
  }

  function initShell(activePage) {
    if (!global.BaklavaAuth.requireAuth()) return;
    renderNav(activePage);
    // Translate any static markup on the page after the shell is ready.
    global.BaklavaI18n.apply();
  }

  global.BaklavaShell = { initShell };
})(window);
