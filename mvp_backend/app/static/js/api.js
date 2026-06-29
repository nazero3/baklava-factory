(function (global) {
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

  async function request(path, method, body) {
    const headers = { "Content-Type": "application/json" };
    const token = global.BaklavaAuth.getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    const res = await fetch(path, {
      method,
      headers,
      body: body != null ? JSON.stringify(body) : null,
    });

    if (res.status === 401 && global.BaklavaAuth.getRefreshToken()) {
      try {
        await global.BaklavaAuth.refresh();
        headers.Authorization = `Bearer ${global.BaklavaAuth.getAccessToken()}`;
        const retry = await fetch(path, {
          method,
          headers,
          body: body != null ? JSON.stringify(body) : null,
        });
        return parseResponse(retry);
      } catch {
        global.BaklavaAuth.clearTokens();
        window.location.href = "/login";
        throw new Error("Session expired. Please log in again.");
      }
    }

    return parseResponse(res);
  }

  global.BaklavaApi = {
    get: (path) => request(path, "GET"),
    post: (path, body) => request(path, "POST", body),
  };
})(window);
