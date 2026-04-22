const elements = {
  tierSelect: document.getElementById("tierSelect"),
  autoRefresh: document.getElementById("autoRefresh"),
  refreshButton: document.getElementById("refreshButton"),
  screenRows: document.getElementById("screenRows"),
  screenTitle: document.getElementById("screenTitle"),
  profileName: document.getElementById("profileName"),
  modeBadge: document.getElementById("modeBadge"),
  surfaceBadge: document.getElementById("surfaceBadge"),
  stateSummary: document.getElementById("stateSummary"),
  surfaceLines: document.getElementById("surfaceLines"),
  artifactList: document.getElementById("artifactList"),
  companionList: document.getElementById("companionList"),
  logLines: document.getElementById("logLines"),
  commandHints: document.getElementById("commandHints"),
  commandForm: document.getElementById("commandForm"),
  commandInput: document.getElementById("commandInput"),
};

let rowNodes = [];
let rowSignatures = [];
let pollTimer = null;
let activeTier = null;

async function fetchFrame() {
  const url = activeTier ? `/api/frame?tier=${encodeURIComponent(activeTier)}` : "/api/frame";
  const response = await fetch(url, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Frame request failed: ${response.status}`);
  }
  return response.json();
}

async function postCommand(command) {
  const response = await fetch("/api/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      command,
      tier: activeTier,
    }),
  });
  if (!response.ok) {
    throw new Error(`Command request failed: ${response.status}`);
  }
  return response.json();
}

function renderFrame(payload) {
  applyTheme(payload.theme);
  renderGrid(payload.grid);
  renderMeta(payload);
}

function applyTheme(theme) {
  if (!theme || !theme.colors) {
    return;
  }

  const root = document.documentElement;
  root.style.setProperty("--signal", theme.colors.signalPrimary);
  root.style.setProperty("--structure", theme.colors.structuralDim);
  root.style.setProperty("--accent", theme.colors.accentRare);
  root.style.setProperty("--bg", theme.colors.background);
}

function renderGrid(grid) {
  if (!grid || !Array.isArray(grid.rows)) {
    return;
  }

  const rowCount = grid.rows.length;
  while (rowNodes.length < rowCount) {
    const rowNode = document.createElement("div");
    rowNode.className = "screen-row";
    rowNodes.push(rowNode);
    elements.screenRows.appendChild(rowNode);
    rowSignatures.push("");
  }

  while (rowNodes.length > rowCount) {
    const rowNode = rowNodes.pop();
    rowNode.remove();
    rowSignatures.pop();
  }

  grid.rows.forEach((row, index) => {
    if (rowSignatures[index] === row.signature) {
      return;
    }

    const rowNode = rowNodes[index];
    rowNode.replaceChildren();
    for (const run of row.runs) {
      const span = document.createElement("span");
      span.className = `style-${(run.style || "none").replace(/[^a-z_]/g, "_")}`;
      span.textContent = run.text;
      rowNode.appendChild(span);
    }
    rowSignatures[index] = row.signature;
  });
}

function renderMeta(payload) {
  const shell = payload.shell || {};
  const renderState = payload.renderState || {};
  const profile = payload.profile || {};
  const transition = shell.activeTransition;
  const scene = payload.scene || {};

  elements.profileName.textContent = profile.displayName || profile.id || "Unknown";
  elements.screenTitle.textContent = `${profile.displayName || "Companion"} shell preview`;
  elements.modeBadge.textContent = shell.modeId || "standby";
  elements.surfaceBadge.textContent = shell.surfaceFocus || "memory";
  activeTier = shell.capabilityTier || activeTier || elements.tierSelect.value;
  elements.tierSelect.value = activeTier;

  const stateLines = [
    `profile ${profile.id || "unknown"}`,
    `tier ${shell.capabilityTier || "pure-text"}`,
    `grid ${renderState.scene?.grid?.width || "?"}x${renderState.scene?.grid?.height || "?"}`,
    `motions ${scene.layers?.join(" / ") || "n/a"}`,
  ];
  if (transition) {
    stateLines.push(
      `transition ${transition.sourceModeId} -> ${transition.targetModeId} ${Math.round((transition.progress || 0) * 100)}%`
    );
  }
  elements.stateSummary.textContent = stateLines.join("\n");

  elements.surfaceLines.textContent = (shell.surface?.lines || []).join("\n") || "No active surface lines.";
  elements.artifactList.textContent = formatArtifacts(shell.visibleArtifacts || []);
  elements.companionList.textContent = (shell.visibleCompanions || [])
    .map((item) => item.name || item.id)
    .join("\n") || "No visible companions.";

  const recentLog = (shell.transmissionLog || []).slice(-8);
  elements.logLines.textContent = recentLog
    .map((entry) => `${entry.speaker}> ${entry.text}`)
    .join("\n") || "No transmissions yet.";

  elements.commandHints.textContent = (shell.commandHints || []).join("\n") || "No command hints.";
}

function formatArtifacts(artifacts) {
  if (!artifacts.length) {
    return "No visible artifacts.";
  }
  return artifacts
    .map((artifact) => {
      const source = artifact.sourceMemoryIds?.[0] || "seed";
      const target = artifact.visualBinding?.target || "shell";
      return `${artifact.title}\n${artifact.type.replace("artifact.", "")} -> ${target} from ${source}`;
    })
    .join("\n\n");
}

async function refresh() {
  try {
    const payload = await fetchFrame();
    renderFrame(payload);
  } catch (error) {
    elements.stateSummary.textContent = String(error);
  }
}

function restartPolling() {
  if (pollTimer !== null) {
    clearInterval(pollTimer);
    pollTimer = null;
  }

  if (elements.autoRefresh.checked) {
    pollTimer = window.setInterval(() => {
      refresh();
    }, 320);
  }
}

elements.refreshButton.addEventListener("click", () => {
  refresh();
});

elements.autoRefresh.addEventListener("change", () => {
  restartPolling();
});

elements.tierSelect.addEventListener("change", () => {
  activeTier = elements.tierSelect.value;
  rowSignatures = rowSignatures.map(() => "");
  refresh();
});

elements.commandForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const command = elements.commandInput.value.trim();
  if (!command) {
    return;
  }

  try {
    const payload = await postCommand(command);
    renderFrame(payload);
    elements.commandInput.value = "";
  } catch (error) {
    elements.stateSummary.textContent = String(error);
  }
});

restartPolling();
refresh();
