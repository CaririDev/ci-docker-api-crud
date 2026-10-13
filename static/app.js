const form = document.querySelector("#item-form");
const itemId = document.querySelector("#item-id");
const itemName = document.querySelector("#item-name");
const itemDescription = document.querySelector("#item-description");
const itemStatus = document.querySelector("#item-status");
const itemsList = document.querySelector("#items-list");
const emptyState = document.querySelector("#empty-state");
const feedback = document.querySelector("#feedback");
const cancelButton = document.querySelector("#cancel-button");
const saveButton = document.querySelector("#save-button");
const formTitle = document.querySelector("#form-title");
const formKicker = document.querySelector("#form-kicker");
const operationBadge = document.querySelector("#operation-badge");

function showFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.classList.toggle("error", isError);
  if (message) window.setTimeout(() => { feedback.textContent = ""; }, 3500);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(data?.error || "Não foi possível concluir a operação.");
  return data;
}

function statusClass(status) {
  if (status === "Concluído") return "done";
  if (status === "Em andamento") return "progress";
  return "pending";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderItems(items) {
  document.querySelector("#total-items").textContent = items.length;
  document.querySelector("#completed-items").textContent = items.filter((item) => item.status === "Concluído").length;
  document.querySelector("#progress-items").textContent = items.filter((item) => item.status === "Em andamento").length;
  emptyState.classList.toggle("hidden", items.length > 0);
  itemsList.innerHTML = items.map((item) => `
    <article class="item-card">
      <div class="item-main">
        <h3 class="item-name" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</h3>
        <p class="item-description" title="${escapeHtml(item.description)}">${escapeHtml(item.description || "Sem descrição")}</p>
        <div class="item-meta">
          <span class="badge ${statusClass(item.status)}">${escapeHtml(item.status)}</span>
          <span>#${item.id}</span>
        </div>
      </div>
      <div class="item-actions">
        <button class="icon-button" type="button" title="Editar item" data-action="edit" data-id="${item.id}">✎</button>
        <button class="icon-button delete" type="button" title="Excluir item" data-action="delete" data-id="${item.id}">×</button>
      </div>
    </article>
  `).join("");
}

async function loadItems() {
  try {
    const data = await api("/api/items");
    renderItems(data.items);
  } catch (error) {
    showFeedback(error.message, true);
  }
}

function resetForm() {
  form.reset();
  itemId.value = "";
  formKicker.textContent = "NOVO REGISTRO";
  formTitle.textContent = "Adicionar item";
  operationBadge.textContent = "POST";
  saveButton.textContent = "Adicionar item";
  cancelButton.classList.add("hidden");
}

async function editItem(id) {
  try {
    const item = await api(`/api/items/${id}`);
    itemId.value = item.id;
    itemName.value = item.name;
    itemDescription.value = item.description;
    itemStatus.value = item.status;
    formKicker.textContent = `EDITANDO ITEM #${item.id}`;
    formTitle.textContent = "Atualizar item";
    operationBadge.textContent = "PUT";
    saveButton.textContent = "Salvar alterações";
    cancelButton.classList.remove("hidden");
    itemName.focus();
  } catch (error) {
    showFeedback(error.message, true);
  }
}

async function deleteItem(id) {
  if (!window.confirm(`Excluir o item #${id}?`)) return;
  try {
    await api(`/api/items/${id}`, { method: "DELETE" });
    showFeedback("Item excluído com sucesso.");
    if (itemId.value === String(id)) resetForm();
    await loadItems();
  } catch (error) {
    showFeedback(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = itemId.value;
  const payload = { name: itemName.value, description: itemDescription.value, status: itemStatus.value };
  try {
    await api(id ? `/api/items/${id}` : "/api/items", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    showFeedback(id ? "Item atualizado com sucesso." : "Item criado com sucesso.");
    resetForm();
    await loadItems();
  } catch (error) {
    showFeedback(error.message, true);
  }
});

itemsList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;
  if (button.dataset.action === "edit") editItem(id);
  if (button.dataset.action === "delete") deleteItem(id);
});

cancelButton.addEventListener("click", resetForm);
document.querySelector("#refresh-button").addEventListener("click", loadItems);
loadItems();
