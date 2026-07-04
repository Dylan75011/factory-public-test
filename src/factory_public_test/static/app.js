const state = {
  dashboard: null,
};

const statusOptions = ["todo", "doing", "blocked", "done"];

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

async function loadDashboard() {
  state.dashboard = await requestJson("/api/dashboard");
  renderDashboard();
}

function renderDashboard() {
  const { totals, projects, work_items: workItems } = state.dashboard;
  document.querySelector("#total-projects").textContent = totals.projects;
  document.querySelector("#open-tasks").textContent = totals.open_tasks;
  document.querySelector("#blocked-tasks").textContent = totals.blocked_tasks;
  document.querySelector("#total-points").textContent = totals.points;
  renderProjects(projects);
  renderProjectOptions(projects);
  renderTasks(projects, workItems);
}

function renderProjects(projects) {
  const list = document.querySelector("#project-list");
  list.innerHTML = "";

  if (projects.length === 0) {
    list.innerHTML = '<div class="empty-state">No projects yet.</div>';
    return;
  }

  for (const project of projects) {
    const card = document.createElement("article");
    card.className = "project-card";
    card.innerHTML = `
      <h3>${escapeHtml(project.name)}</h3>
      <p>${escapeHtml(project.description || "No description")}</p>
      <div class="project-meta">
        <span class="pill pill-${project.status}">${project.status}</span>
        <span class="pill">${escapeHtml(project.owner)}</span>
        <span class="pill">${project.open_count} open</span>
        <span class="pill">${project.points} pts</span>
      </div>
    `;
    list.appendChild(card);
  }
}

function renderProjectOptions(projects) {
  const select = document.querySelector("#task-project-select");
  const currentValue = select.value;
  select.innerHTML = "";

  for (const project of projects) {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.name;
    select.appendChild(option);
  }

  if (currentValue) {
    select.value = currentValue;
  }
}

function renderTasks(projects, workItems) {
  const table = document.querySelector("#task-table");
  table.innerHTML = "";
  const projectNames = new Map(projects.map((project) => [project.id, project.name]));

  if (workItems.length === 0) {
    table.innerHTML = '<tr><td colspan="6">No tasks yet.</td></tr>';
    return;
  }

  for (const item of workItems) {
    const row = document.createElement("tr");
    const options = statusOptions
      .map((status) => {
        const selected = status === item.status ? "selected" : "";
        return `<option value="${status}" ${selected}>${status}</option>`;
      })
      .join("");

    row.innerHTML = `
      <td>${escapeHtml(item.title)}</td>
      <td>${escapeHtml(projectNames.get(item.project_id) || "Unknown")}</td>
      <td>${escapeHtml(item.assignee || "Unassigned")}</td>
      <td><span class="pill pill-${item.priority}">${item.priority}</span></td>
      <td>
        <select class="status-select" data-task-id="${item.id}">
          ${options}
        </select>
      </td>
      <td>${item.points}</td>
    `;
    table.appendChild(row);
  }
}

async function createProject(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());
  await requestJson("/api/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
  form.reset();
  await loadDashboard();
}

async function createTask(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());
  data.project_id = Number(data.project_id);
  data.points = Number(data.points || 1);
  await requestJson("/api/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
  form.reset();
  await loadDashboard();
}

async function updateTaskStatus(event) {
  const select = event.target.closest(".status-select");
  if (!select) {
    return;
  }

  await requestJson(`/api/tasks/${select.dataset.taskId}`, {
    method: "PATCH",
    body: JSON.stringify({ status: select.value }),
  });
  await loadDashboard();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.querySelector("#refresh-button").addEventListener("click", loadDashboard);
document.querySelector("#project-form").addEventListener("submit", createProject);
document.querySelector("#task-form").addEventListener("submit", createTask);
document.querySelector("#task-table").addEventListener("change", updateTaskStatus);

loadDashboard().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><p>${escapeHtml(error.message)}</p></main>`;
});

