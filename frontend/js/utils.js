export function getToken() {
    return localStorage.getItem("access_token");
}

export function setTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}

export function parseJwt(token) {
    try { return JSON.parse(atob(token.split(".")[1])); } catch { return {}; }
}

export function isLoggedIn() {
    return !!getToken();
}

export function isAdmin() {
    const token = getToken();
    if (!token) return false;
    return parseJwt(token).role === "admin";
}

export function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = rootPath() + "auth.html";
    }
}

export function requireAdmin() {
    if (!isLoggedIn()) {
        window.location.href = rootPath() + "auth.html";
        return;
    }
    if (!isAdmin()) {
        window.location.href = rootPath() + "errors/403.html";
        return;
    }
    document.body.style.visibility = "visible";
}

export function hideUntilReady() {
    document.body.style.visibility = "hidden";
}

export function rootPath() {
    const path = window.location.pathname;
    return path.includes("/admin/") ? "../" : "./";
}

export function showConfirm(message, title = "Подтверждение") {
    return new Promise(resolve => {
        const overlay = document.createElement("div");
        overlay.className = "confirm-overlay";
        overlay.innerHTML = `
            <div class="confirm-box">
                <span class="confirm-icon">🗑️</span>
                <div class="confirm-title">${title}</div>
                <p class="confirm-text">${message}</p>
                <div class="confirm-btns">
                    <button class="btn btn-secondary" id="confirm-cancel">Отмена</button>
                    <button class="btn btn-danger"    id="confirm-ok">Удалить</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        const close = (result) => { overlay.remove(); resolve(result); };
        overlay.querySelector("#confirm-ok").addEventListener("click", () => close(true));
        overlay.querySelector("#confirm-cancel").addEventListener("click", () => close(false));
        overlay.addEventListener("click", e => { if (e.target === overlay) close(false); });
    });
}

export function showAlert(container, msg, type = "error") {
    const el = document.createElement("div");
    el.className = `alert alert-${type}`;
    el.textContent = msg;
    container.prepend(el);
    setTimeout(() => el.remove(), 4000);
}

export function renderNav(adminLinks = false) {
    const root = rootPath();
    const logged = isLoggedIn();
    const admin = isAdmin();

    const publicLinks = `
        <a href="${root}index.html">Главная</a>
    `;

    const userLinks = logged ? `
        <a href="${root}profile.html">Профиль</a>
        ${admin ? `<a href="${root}admin/users.html">Админка</a>` : ""}
        <a href="#" id="nav-logout">Выйти</a>
    ` : `
        <a href="${root}auth.html">Войти</a>
    `;

    const adminSidebar = adminLinks && admin ? `
        <div class="admin-sidebar-links">
            <a href="${root}admin/users.html">Пользователи</a>
            <a href="${root}admin/styles.html">Стили</a>
            <a href="${root}admin/teachers.html">Преподаватели</a>
        </div>
    ` : "";

    const nav = document.getElementById("nav");
    if (nav) {
        nav.innerHTML = `
            <a class="nav-brand" href="${root}index.html">
                <img src="${root}images/logo_78.png" alt="Семь-Восемь" class="nav-logo">
            </a>
            <div class="nav-links">
                ${publicLinks}
                ${userLinks}
            </div>
            ${adminSidebar}
        `;

        const logoutBtn = document.getElementById("nav-logout");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", (e) => {
                e.preventDefault();
                clearTokens();
                window.location.href = root + "auth.html";
            });
        }

        // Highlight active link
        const current = window.location.pathname.split("/").pop() || "index.html";
        nav.querySelectorAll("a").forEach(a => {
            if (a.href.endsWith(current)) a.classList.add("active");
        });
    }
}
