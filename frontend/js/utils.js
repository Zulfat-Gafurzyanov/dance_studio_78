export function getToken() {
    return localStorage.getItem("access_token");
}

export function setTokens(access) {
    localStorage.setItem("access_token", access);
}

export function clearTokens() {
    localStorage.removeItem("access_token");
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
        window.location.href = rootPath() + "auth";
    }
}

export function requireAdmin() {
    if (!isLoggedIn()) {
        window.location.href = rootPath() + "auth";
        return;
    }
    if (!isAdmin()) {
        window.location.href = rootPath() + "errors/403";
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

export function renderSidebar() {
    const el = document.getElementById('admin-sidebar');
    if (!el) return;
    const links = [
        ['users',    'Пользователи'],
        ['styles',   'Стили'],
        ['teachers', 'Преподаватели'],
        ['prices',   'Цены'],
        ['studio',   'Студия'],
        ['schedule', 'Расписание'],
    ];
    const current = window.location.pathname.split('/').pop();
    el.innerHTML = '<h3>Управление</h3>' +
        links.map(([href, label]) =>
            `<a href="${href}"${current === href ? ' class="active"' : ''}>${label}</a>`
        ).join('');
}

export function renderNav(centerLinks = null, leftLinks = null) {
    const root        = rootPath();
    const logged      = isLoggedIn();
    const admin       = isAdmin();
    const isAdminPage = window.location.pathname.includes('/admin/');

    const userLinks = logged ? `
        ${!isAdminPage && admin ? `<a href="${root}admin/users">Админка</a>` : ""}
        <a href="${root}profile">Профиль</a>
    ` : `<a href="${root}auth" class="btn-nav">Войти</a>`;

    const defaultLinks = [{href: root, text: 'Главная'}];
    const links = centerLinks || defaultLinks;

    const leftHtml = leftLinks
        ? `<div class="nav-left-links">${leftLinks.map(l => `<a href="${l.href}">${l.text}</a>`).join('')}</div>`
        : '';

    const centerHtml = isAdminPage
        ? `<span class="nav-admin-zone">АДМИН-ЗОНА</span>`
        : `<div class="nav-section-links">${links.map(l => `<a href="${l.href}">${l.text}</a>`).join('')}</div>`;

    const nav = document.getElementById("nav");
    if (nav) {
        nav.innerHTML = `
            <a class="nav-brand" href="${root}">
                <img src="${root}images/logo_78.png" alt="Семь-Восемь" class="nav-logo">
            </a>
            ${leftHtml}
            ${centerHtml}
            <div class="nav-auth">${userLinks}</div>
        `;

        const logoutBtn = document.getElementById("nav-logout");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", async (e) => {
                e.preventDefault();
                await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" }).catch(() => {});
                clearTokens();
                window.location.href = root + "auth";
            });
        }

        // Highlight active link
        const current = window.location.pathname.split("/").pop() || "index";
        nav.querySelectorAll("a").forEach(a => {
            if (a.href.endsWith(current)) a.classList.add("active");
        });
    }
}
