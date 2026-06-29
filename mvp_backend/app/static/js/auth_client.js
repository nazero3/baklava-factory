(function (global) {
  const ACCESS_TOKEN_KEY = "baklava_access_token";
  const REFRESH_TOKEN_KEY = "baklava_refresh_token";
  const ROLE_KEY = "baklava_role";
  const USERNAME_KEY = "baklava_username";

  async function parseResponse(res) {
    const txt = await res.text();
    let data;
    try {
      data = txt ? JSON.parse(txt) : {};
    } catch {
      data = { raw: txt };
    }
    if (!res.ok) {
      const detail = data.detail;
      const message =
        typeof detail === "string"
          ? detail
          : detail != null
            ? JSON.stringify(detail)
            : `HTTP ${res.status}`;
      throw new Error(message);
    }
    return data;
  }

  function storeTokens(accessToken, refreshToken, role, username) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken !== undefined) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
    if (role) localStorage.setItem(ROLE_KEY, role);
    if (username) localStorage.setItem(USERNAME_KEY, username);
  }

  function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  function getRole() {
    return localStorage.getItem(ROLE_KEY) || "";
  }

  function getUsername() {
    return localStorage.getItem(USERNAME_KEY) || "";
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(USERNAME_KEY);
  }

  function isLoggedIn() {
    return Boolean(getAccessToken());
  }

  async function login(username, password) {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await parseResponse(res);
    storeTokens(data.access_token, data.refresh_token, data.role, username);
    return data;
  }

  async function refresh() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token stored");
    const res = await fetch("/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const data = await parseResponse(res);
    storeTokens(data.access_token, undefined, data.role);
    return data;
  }

  async function logout() {
    const accessToken = getAccessToken();
    try {
      if (accessToken) {
        const res = await fetch("/auth/logout", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        });
        await parseResponse(res);
      }
    } finally {
      clearTokens();
    }
  }

  function requireAuth() {
    if (!isLoggedIn()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  }

  global.BaklavaAuth = {
    login,
    logout,
    refresh,
    getAccessToken,
    getRefreshToken,
    getRole,
    getUsername,
    isLoggedIn,
    requireAuth,
    clearTokens,
  };
})(window);
