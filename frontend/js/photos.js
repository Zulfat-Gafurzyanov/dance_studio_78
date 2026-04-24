import { showAlert } from "./utils.js";

/**
 * Строит HTML-блок фото для item-card.
 * @param {Array}  photos   - массив объектов { id, url, sort_order }
 * @param {number} entityId - id стиля или преподавателя
 * @param {string} delFn    - имя window-функции для удаления фото
 */
export function buildPhotoGrid(photos, entityId, delFn) {
    const sorted = [...photos].sort((a, b) => a.sort_order - b.sort_order);
    return `
        <div class="photo-grid" data-id="${entityId}">
            ${sorted.map(p => `
                <div class="photo-thumb" draggable="true" data-photo-id="${p.id}">
                    <img src="${p.url}" onerror="this.style.background='var(--card)';this.removeAttribute('src')">
                    <button class="photo-del" onclick="${delFn}(${p.id})" title="Удалить">×</button>
                    <span class="photo-order"></span>
                </div>
            `).join("")}
        </div>
    `;
}

/**
 * Инициализирует drag-and-drop для всех .photo-grid на странице.
 * @param {Function} updateFn - (photoId, sort_order) => Promise  — API-метод обновления
 * @param {Element}  alertContainer - контейнер для showAlert при ошибке
 */
export function initPhotoGrids(updateFn, alertContainer) {
    document.querySelectorAll(".photo-grid").forEach(grid => {
        let dragged = null;

        const refreshNumbers = () =>
            grid.querySelectorAll(".photo-thumb").forEach((t, i) =>
                t.querySelector(".photo-order").textContent = i + 1
            );

        refreshNumbers();

        grid.querySelectorAll(".photo-thumb").forEach(thumb => {
            thumb.addEventListener("dragstart", () => {
                dragged = thumb;
                setTimeout(() => thumb.classList.add("dragging"), 0);
            });

            thumb.addEventListener("dragend", () => {
                thumb.classList.remove("dragging");
                dragged = null;
            });

            thumb.addEventListener("dragover", e => {
                e.preventDefault();
                if (dragged && dragged !== thumb) thumb.classList.add("drag-over");
            });

            thumb.addEventListener("dragleave", () =>
                thumb.classList.remove("drag-over")
            );

            thumb.addEventListener("drop", async e => {
                e.preventDefault();
                thumb.classList.remove("drag-over");
                if (!dragged || dragged === thumb) return;

                const all = [...grid.querySelectorAll(".photo-thumb")];
                const fromIdx = all.indexOf(dragged);
                const toIdx   = all.indexOf(thumb);
                if (fromIdx < toIdx) thumb.after(dragged);
                else thumb.before(dragged);

                const updated = [...grid.querySelectorAll(".photo-thumb")];
                refreshNumbers();

                try {
                    await Promise.all(updated.map((t, i) =>
                        updateFn(+t.dataset.photoId, i + 1)
                    ));
                } catch (err) {
                    showAlert(alertContainer, err.message);
                }
            });
        });
    });
}
