const BASE_URL = window.location.hostname === "localhost"
    ? "http://localhost:8000/api/v1"
    : "/api/v1";

function getToken() {
    return localStorage.getItem("access_token");
}

async function doRequest(method, path, body, token) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });
}

function errorsPath() {
    return window.location.pathname.includes("/admin/") ? "../errors/" : "./errors/";
}

async function request(method, path, body = null, auth = true) {
    let res;
    try {
        res = await doRequest(method, path, body, auth ? getToken() : null);
    } catch {
        window.location.href = errorsPath() + "503";
        return;
    }

    if (res.status === 204) return null;

    if (res.status === 403) { window.location.href = errorsPath() + "403"; return; }
    if (res.status === 500) { window.location.href = errorsPath() + "500"; return; }
    if (res.status === 503) { window.location.href = errorsPath() + "503"; return; }

    // Автоматический рефреш при истёкшем access token
    if (res.status === 401 && auth) {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
            localStorage.removeItem("access_token");
            window.location.href = (window.location.pathname.includes("/admin/") ? "../" : "./") + "auth";
            return;
        }
        try {
            const refreshRes = await doRequest("POST", "/auth/refresh", { refresh_token: refreshToken }, null);
            if (!refreshRes.ok) throw new Error();
            const tokens = await refreshRes.json();
            localStorage.setItem("access_token", tokens.access_token);
            if (tokens.refresh_token) localStorage.setItem("refresh_token", tokens.refresh_token);

            // Повторяем исходный запрос с новым токеном
            const retry = await doRequest(method, path, body, tokens.access_token);
            if (retry.status === 204) return null;
            const retryData = await retry.json().catch(() => null);
            if (!retry.ok) throw new Error(retryData?.detail || `HTTP ${retry.status}`);
            return retryData;
        } catch {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = (window.location.pathname.includes("/admin/") ? "../" : "./") + "auth";
            return;
        }
    }

    const data = await res.json().catch(() => null);
    if (!res.ok) {
        const detail = Array.isArray(data?.detail)
            ? data.detail.map(e => e.msg).join(", ")
            : data?.detail || `HTTP ${res.status}`;
        throw new Error(detail);
    }
    return data;
}

export const api = {
    // Auth
    signUp: (email, password, password_confirm) =>
        request("POST", "/auth/sign-up", { email, password, password_confirm }, false),
    signIn: (email, password) =>
        request("POST", "/auth/sign-in", { email, password }, false),
    refresh: () =>
        request("POST", "/auth/refresh", { refresh_token: localStorage.getItem("refresh_token") }, false),

    // Users
    getMe: () => request("GET", "/users/me"),
    updateMe: (data) => request("PATCH", "/users/me", data),
    deleteMe: () => request("DELETE", "/users/me"),

    // Admin
    getUsers: () => request("GET", "/admin/users"),
    updateRole: (id, role) => request("PATCH", `/admin/users/${id}/role`, { role }),
    updateActive: (id, is_active) => request("PATCH", `/admin/users/${id}/active`, { is_active }),

    // Styles
    getStyles: () => request("GET", "/styles", null, false),
    createStyle: (data) => request("POST", "/styles", data),
    updateStyle: (id, data) => request("PATCH", `/styles/${id}`, data),
    deleteStyle: (id) => request("DELETE", `/styles/${id}`),
    addStyleImage: (id, data) => request("POST", `/styles/${id}/images`, data),
    updateStyleImage: (id, sort_order) => request("PATCH", `/styles/images/${id}`, { sort_order }),
    deleteStyleImage: (id) => request("DELETE", `/styles/images/${id}`),

    // Teachers
    getTeachers: () => request("GET", "/teachers", null, false),
    createTeacher: (data) => request("POST", "/teachers", data),
    updateTeacher: (id, data) => request("PATCH", `/teachers/${id}`, data),
    deleteTeacher: (id) => request("DELETE", `/teachers/${id}`),
    reorderTeachers: (items) => request("PUT", "/teachers/reorder", items),
    addTeacherPhoto: (id, data) => request("POST", `/teachers/${id}/photos`, data),
    updateTeacherPhoto: (id, sort_order) => request("PATCH", `/teachers/photos/${id}`, { sort_order }),
    deleteTeacherPhoto: (id) => request("DELETE", `/teachers/photos/${id}`),

    // Prices
    getPrices: () => request("GET", "/prices", null, false),
    createPrice: (data) => request("POST", "/prices", data),
    updatePrice: (id, data) => request("PATCH", `/prices/${id}`, data),
    deletePrice: (id) => request("DELETE", `/prices/${id}`),
    addPriceOption: (id, data) => request("POST", `/prices/${id}/options`, data),
    deletePriceOption: (id) => request("DELETE", `/prices/options/${id}`),

    // Studio info
    getStudioInfo: () => request("GET", "/studio-info", null, false),
    updateStudioInfo: (data) => request("PATCH", "/studio-info", data),

    // Health
    health: () => request("GET", "/health", null, false),
};
