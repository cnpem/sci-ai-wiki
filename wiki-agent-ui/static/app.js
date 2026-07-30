const messagesElement = document.querySelector("#messages");
const emptyState = document.querySelector("#empty-state");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send");
const statusElement = document.querySelector("#status");
const newChatButton = document.querySelector("#new-chat");
const engineSelect = document.querySelector("#engine");
const workspaceShell = document.querySelector("#workspace-shell");
const viewer = document.querySelector("#wiki-viewer");
const viewerResizer = document.querySelector("#viewer-resizer");
const viewerTitle = document.querySelector("#viewer-title");
const viewerContent = document.querySelector("#viewer-content");
const closeViewerButton = document.querySelector("#close-viewer");
const attachPdfButton = document.querySelector("#attach-pdf");
const pdfInput = document.querySelector("#pdf-input");
const attachmentTray = document.querySelector("#attachment-tray");
const attachmentStatus = document.querySelector("#attachment-status");

let history = [];
let busy = false;
let uploading = false;
let currentPageId = "";
let currentAnchor = "";
let activeResizePointer = null;
let healthState = null;
let attachments = [];

function createSessionId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 12)}`;
}

let sessionId = createSessionId();

const VIEWER_MIN_WIDTH = 320;
const CHAT_MIN_WIDTH = 420;
const VIEWER_DEFAULT_WIDTH = 470;

function viewerWidthLimits() {
  const shellWidth = workspaceShell.getBoundingClientRect().width;
  return {
    min: VIEWER_MIN_WIDTH,
    max: Math.max(VIEWER_MIN_WIDTH, Math.min(780, shellWidth - CHAT_MIN_WIDTH)),
  };
}

function setViewerWidth(width) {
  const { min, max } = viewerWidthLimits();
  const nextWidth = Math.round(Math.min(max, Math.max(min, width)));
  viewer.style.width = `${nextWidth}px`;
  viewerResizer.setAttribute("aria-valuemin", String(min));
  viewerResizer.setAttribute("aria-valuemax", String(max));
  viewerResizer.setAttribute("aria-valuenow", String(nextWidth));
}

function resizeViewerFromPointer(clientX) {
  const shellRect = workspaceShell.getBoundingClientRect();
  setViewerWidth(shellRect.right - clientX);
}

function finishViewerResize(event) {
  if (activeResizePointer === null) return;
  if (
    event?.pointerId !== undefined &&
    event.pointerId !== activeResizePointer
  ) {
    return;
  }
  activeResizePointer = null;
  document.body.classList.remove("viewer-resizing");
  event?.preventDefault();
}

function updateEngineStatus() {
  if (!healthState) return;
  const engine = healthState.engines?.find(
    (candidate) => candidate.id === engineSelect.value,
  );
  if (!engine?.ready) {
    const unavailableMessages = {
      antigravity: "Antigravity CLI não encontrado",
      opencode: "OpenCode ou Ollama indisponível",
      codex: "Codex CLI não encontrado ou sem login",
    };
    setStatus(unavailableMessages[engineSelect.value], "error");
    return;
  }
  setStatus(`${healthState.documents} páginas · ${engine.label}`, "ready");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderLatex(expression, displayMode = false) {
  const source = String(expression).trim();
  if (!source) return "";
  try {
    if (window.katex?.renderToString) {
      return window.katex.renderToString(source, {
        displayMode,
        throwOnError: false,
        strict: false,
        trust: false,
      });
    }
  } catch {
    // The readable fallback below is intentional.
  }
  return `<code class="math-fallback">${escapeHtml(source)}</code>`;
}

function renderInline(value) {
  const codeTokens = [];
  const mathTokens = [];
  let source = String(value)
    .replace(/\\\((.+?)\\\)/g, (_, expression) => {
      const token = `@@MATH${mathTokens.length}@@`;
      mathTokens.push(renderLatex(expression));
      return token;
    })
    .replace(/\$(?!\$)([^$\n]+?)\$/g, (_, expression) => {
      const token = `@@MATH${mathTokens.length}@@`;
      mathTokens.push(renderLatex(expression));
      return token;
    });

  let html = escapeHtml(source).replace(/`([^`]+)`/g, (_, code) => {
    if (/^\[\[[^\]]+\]\]$/.test(code.trim())) return code.trim();
    const token = `%%CODE_${codeTokens.length}%%`;
    codeTokens.push(`<code>${code}</code>`);
    return token;
  });

  html = html.replace(
    /\[\[([a-zA-Z0-9_./-]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]/g,
    (_, target, anchor, label) => {
      const basename = target.split("/").pop().replace(/\.md$/i, "");
      const anchorAttribute = anchor
        ? ` data-anchor="${escapeHtml(anchor)}"`
        : "";
      return (
        `<button type="button" class="wiki-link" data-page-id="${basename}"` +
        `${anchorAttribute}>${label || `[[${target}${anchor ? `#${anchor}` : ""}]]`}` +
        "</button>"
      );
    },
  );
  html = html.replace(
    /\[([^\]]+)\]\((?!https?:\/\/)([^)#]+?)(?:\.md)?(?:#([^)]+))?\)/g,
    (_, label, target, anchor) => {
      const basename = target.split("/").pop().replace(/\.md$/i, "");
      const anchorAttribute = anchor
        ? ` data-anchor="${escapeHtml(anchor)}"`
        : "";
      return (
        `<button type="button" class="wiki-link" data-page-id="${basename}"` +
        `${anchorAttribute}>${label}</button>`
      );
    },
  );
  html = html.replace(
    /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noreferrer">$1</a>',
  );
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  html = html.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");

  codeTokens.forEach((code, index) => {
    html = html.replace(`%%CODE_${index}%%`, code);
  });
  mathTokens.forEach((math, index) => {
    html = html.replace(`@@MATH${index}@@`, math);
  });
  return html;
}

function renderMarkdown(markdown) {
  let lines = String(markdown || "").replaceAll("\r\n", "\n").split("\n");
  const output = [];
  let paragraph = [];
  let listType = "";
  let inCode = false;
  let codeLanguage = "";
  let codeLines = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      output.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  };
  const closeList = () => {
    if (listType) {
      output.push(`</${listType}>`);
      listType = "";
    }
  };

  if (lines[0]?.trim() === "---") {
    const closingIndex = lines.slice(1).findIndex((line) => line.trim() === "---");
    if (closingIndex >= 0) {
      const metadataLines = lines.slice(1, closingIndex + 1);
      const metadata = metadataLines
        .map((line) => line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/))
        .filter(Boolean);
      if (metadata.length) {
        output.push(
          '<details class="frontmatter"><summary>Metadados</summary><dl>' +
            metadata
              .map(
                ([, key, value]) =>
                  `<dt>${escapeHtml(key.replaceAll("_", " "))}</dt>` +
                  `<dd>${renderInline(value)}</dd>`,
              )
              .join("") +
            "</dl></details>",
        );
      }
      lines = lines.slice(closingIndex + 2);
    }
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmedLine = line.trim();

    if (trimmedLine.startsWith("$$") || trimmedLine.startsWith("\\[")) {
      flushParagraph();
      closeList();
      const isDollarBlock = trimmedLine.startsWith("$$");
      const opening = isDollarBlock ? "$$" : "\\[";
      const closing = isDollarBlock ? "$$" : "\\]";
      let expression = trimmedLine.slice(opening.length);

      if (expression.endsWith(closing)) {
        expression = expression.slice(0, -closing.length);
      } else {
        const expressionLines = [expression];
        while (index + 1 < lines.length) {
          index += 1;
          const mathLine = lines[index];
          if (mathLine.trim().endsWith(closing)) {
            expressionLines.push(
              mathLine.slice(0, mathLine.lastIndexOf(closing)),
            );
            break;
          }
          expressionLines.push(mathLine);
        }
        expression = expressionLines.join("\n");
      }
      output.push(
        `<div class="math-block">${renderLatex(expression, true)}</div>`,
      );
      continue;
    }

    if (line.trim().startsWith("```")) {
      flushParagraph();
      closeList();
      if (!inCode) {
        inCode = true;
        codeLanguage = line.trim().slice(3).trim();
        codeLines = [];
      } else {
        output.push(
          `<pre data-language="${escapeHtml(codeLanguage)}"><code>` +
            `${escapeHtml(codeLines.join("\n"))}</code></pre>`,
        );
        inCode = false;
      }
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }

    const nextLine = lines[index + 1] || "";
    if (
      line.includes("|") &&
      /^\s*\|?[\s:-]+\|[\s|:-]*\|?\s*$/.test(nextLine)
    ) {
      flushParagraph();
      closeList();
      const cells = (row) =>
        row
          .trim()
          .replace(/^\||\|$/g, "")
          .split("|")
          .map((cell) => cell.trim());
      const headers = cells(line);
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|")) {
        rows.push(cells(lines[index]));
        index += 1;
      }
      index -= 1;
      output.push(
        "<div class=\"table-wrap\"><table><thead><tr>" +
          headers.map((cell) => `<th>${renderInline(cell)}</th>`).join("") +
          "</tr></thead><tbody>" +
          rows
            .map(
              (row) =>
                "<tr>" +
                row.map((cell) => `<td>${renderInline(cell)}</td>`).join("") +
                "</tr>",
            )
            .join("") +
          "</tbody></table></div>",
      );
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      closeList();
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      closeList();
      const level = heading[1].length;
      const headingId = heading[2]
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");
      output.push(
        `<h${level} id="${headingId}">${renderInline(heading[2])}</h${level}>`,
      );
      continue;
    }

    if (/^\s*([-*_])(?:\s*\1){2,}\s*$/.test(line)) {
      flushParagraph();
      closeList();
      output.push("<hr>");
      continue;
    }

    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const nextType = unordered ? "ul" : "ol";
      if (listType !== nextType) {
        closeList();
        listType = nextType;
        output.push(`<${listType}>`);
      }
      output.push(`<li>${renderInline((unordered || ordered)[1])}</li>`);
      continue;
    }

    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) {
      flushParagraph();
      closeList();
      output.push(`<blockquote>${renderInline(quote[1])}</blockquote>`);
      continue;
    }

    paragraph.push(line.trim());
  }

  if (inCode) {
    output.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
  }
  flushParagraph();
  closeList();
  return output.join("");
}

function setStatus(text, state = "") {
  statusElement.textContent = text;
  statusElement.className = `status ${state}`.trim();
}

function hideEmptyState() {
  if (emptyState) emptyState.hidden = true;
}

function scrollToBottom() {
  messagesElement.scrollTop = messagesElement.scrollHeight;
}

function setAttachmentStatus(text = "", state = "") {
  attachmentStatus.textContent = text;
  attachmentStatus.className = `attachment-status ${state}`.trim();
}

function renderAttachments() {
  attachmentTray.replaceChildren();
  attachmentTray.hidden = attachments.length === 0;

  attachments.forEach((attachment) => {
    const chip = document.createElement("div");
    chip.className = "attachment-chip";

    const label = document.createElement("span");
    label.className = "attachment-chip-label";
    label.textContent = attachment.filename;
    label.title = attachment.filename;

    const meta = document.createElement("span");
    meta.className = "attachment-chip-meta";
    meta.textContent = `${attachment.pages} p.`;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "attachment-remove";
    remove.setAttribute("aria-label", `Remover ${attachment.filename}`);
    remove.title = "Remover PDF";
    remove.textContent = "×";
    remove.addEventListener("click", () => removeAttachment(attachment.id));

    chip.append(label, meta, remove);
    attachmentTray.appendChild(chip);
  });
}

async function uploadPdf(file) {
  if (!file) return;
  if (
    file.type !== "application/pdf" &&
    !file.name.toLowerCase().endsWith(".pdf")
  ) {
    setAttachmentStatus("Escolha um arquivo PDF.", "error");
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    setAttachmentStatus("O PDF deve ter no máximo 20 MB.", "error");
    return;
  }
  if (attachments.length >= 5) {
    setAttachmentStatus("A conversa aceita até 5 PDFs.", "error");
    return;
  }

  uploading = true;
  attachPdfButton.disabled = true;
  setAttachmentStatus(`Extraindo texto de ${file.name}…`);
  const data = new FormData();
  data.append("session_id", sessionId);
  data.append("file", file);

  try {
    const response = await fetch("/api/attachments", {
      method: "POST",
      body: data,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "Não foi possível anexar o PDF.");
    }
    attachments.push(payload);
    renderAttachments();
    setAttachmentStatus(
      `${payload.filename} pronto para a próxima pergunta.`,
      "ready",
    );
  } catch (error) {
    setAttachmentStatus(error.message, "error");
  } finally {
    uploading = false;
    attachPdfButton.disabled = false;
  }
}

async function removeAttachment(attachmentId) {
  const attachment = attachments.find((item) => item.id === attachmentId);
  try {
    const response = await fetch(
      `/api/attachments/${encodeURIComponent(attachmentId)}` +
        `?session_id=${encodeURIComponent(sessionId)}`,
      { method: "DELETE" },
    );
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "Não foi possível remover o PDF.");
    }
    attachments = attachments.filter((item) => item.id !== attachmentId);
    renderAttachments();
    setAttachmentStatus(
      attachment ? `${attachment.filename} removido.` : "PDF removido.",
    );
  } catch (error) {
    setAttachmentStatus(error.message, "error");
  }
}

function addMessage(
  role,
  content,
  sources = [],
  attachmentSources = [],
) {
  hideEmptyState();
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") {
    bubble.classList.add("markdown-body");
    bubble.innerHTML = renderMarkdown(content);
  } else {
    bubble.textContent = content;
  }
  article.appendChild(bubble);

  if (sources.length || attachmentSources.length) {
    const sourceList = document.createElement("div");
    sourceList.className = "sources";
    sourceList.setAttribute("aria-label", "Fontes citadas");

    sources.forEach((source) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "source";
      chip.dataset.pageId = source.id;
      chip.textContent = source.title || source.id;
      chip.title = `Abrir ${source.path}`;
      sourceList.appendChild(chip);
    });

    attachmentSources.forEach((source) => {
      const chip = document.createElement("span");
      chip.className = "source pdf-source";
      const pages = (source.pages || []).join(", ");
      chip.textContent = `${source.filename} · p. ${pages}`;
      chip.title = "Trecho do PDF temporário usado nesta resposta";
      sourceList.appendChild(chip);
    });
    article.appendChild(sourceList);
  }

  messagesElement.appendChild(article);
  scrollToBottom();
  return article;
}

function addActivity(engine) {
  hideEmptyState();
  const article = document.createElement("article");
  article.className = "message assistant";
  article.dataset.activity = "true";
  article.innerHTML = `
    <div class="agent-activity">
      <div class="activity-heading">
        <span class="activity-pulse" aria-hidden="true"></span>
        <span>${
          engine === "opencode"
            ? "OpenCode trabalhando"
            : engine === "codex"
              ? "Codex trabalhando"
              : "Antigravity trabalhando"
        }</span>
      </div>
      <ul class="activity-list"></ul>
    </div>
  `;
  messagesElement.appendChild(article);
  scrollToBottom();
  return article;
}

function updateActivity(article, phase, message) {
  if (article.querySelector(`[data-phase="${phase}"]`)) return;
  const item = document.createElement("li");
  item.className = "activity-item";
  item.dataset.phase = phase;
  item.textContent = message;
  article.querySelector(".activity-list").appendChild(item);
  scrollToBottom();
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 170)}px`;
}

async function openWikiPage(pageId, anchor = "") {
  if (
    !viewer.hidden &&
    currentPageId === pageId &&
    currentAnchor === anchor
  ) {
    closeViewer();
    return;
  }
  currentPageId = pageId;
  currentAnchor = anchor;
  if (!viewer.style.width) setViewerWidth(VIEWER_DEFAULT_WIDTH);
  viewerResizer.hidden = false;
  viewer.hidden = false;
  viewerTitle.textContent = pageId;
  viewerContent.classList.add("viewer-loading");
  viewerContent.textContent = "Abrindo página…";

  try {
    const response = await fetch(`/api/wiki/${encodeURIComponent(pageId)}`);
    const page = await response.json();
    if (!response.ok) throw new Error(page.detail || "Página não encontrada.");
    viewerTitle.textContent = page.title;
    viewerContent.classList.remove("viewer-loading");
    viewerContent.innerHTML = renderMarkdown(page.content);
    if (anchor) {
      const normalizedAnchor = anchor
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");
      const target = Array.from(viewerContent.querySelectorAll("[id]")).find(
        (element) => element.id === normalizedAnchor,
      );
      target?.scrollIntoView({ block: "start" });
    } else {
      viewerContent.scrollTop = 0;
    }
  } catch (error) {
    viewerContent.classList.remove("viewer-loading");
    viewerContent.textContent = `Erro: ${error.message}`;
  }
}

function closeViewer() {
  finishViewerResize();
  viewerResizer.hidden = true;
  viewer.hidden = true;
  currentPageId = "";
  currentAnchor = "";
}

async function ask(message) {
  if (busy || !message.trim()) return;
  busy = true;
  sendButton.disabled = true;
  engineSelect.disabled = true;

  const previousHistory = history.slice(-10);
  const selectedEngine = engineSelect.value;
  const selectedAttachmentIds = attachments.map(
    (attachment) => attachment.id,
  );
  input.value = "";
  resizeInput();
  input.focus();
  addMessage("user", message);
  history.push({ role: "user", content: message });
  const activity = addActivity(selectedEngine);

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history: previousHistory,
        engine: selectedEngine,
        session_id: sessionId,
        attachment_ids: selectedAttachmentIds,
      }),
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(
        payload.detail || "Não foi possível iniciar o agente selecionado.",
      );
    }
    if (!response.body) throw new Error("O servidor não iniciou a resposta.");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let result = null;

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;
        const event = JSON.parse(line);
        if (event.type === "status") {
          updateActivity(activity, event.phase, event.message);
        } else if (event.type === "result") {
          result = event;
        } else if (event.type === "error") {
          throw new Error(event.message);
        }
      }
      if (done) break;
    }

    if (!result) throw new Error("O agente não retornou uma resposta.");
    activity.remove();
    addMessage(
      "assistant",
      result.answer,
      result.sources || [],
      result.attachment_sources || [],
    );
    history.push({ role: "assistant", content: result.answer });
  } catch (error) {
    activity.remove();
    addMessage("assistant", `**Erro:** ${error.message}`);
  } finally {
    busy = false;
    sendButton.disabled = false;
    engineSelect.disabled = false;
    updateEngineStatus();
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (message) ask(message);
});

attachPdfButton.addEventListener("click", () => {
  if (!uploading) pdfInput.click();
});

pdfInput.addEventListener("change", async () => {
  const selectedFiles = Array.from(pdfInput.files || []);
  pdfInput.value = "";
  for (const file of selectedFiles) {
    await uploadPdf(file);
  }
  input.focus();
});

input.addEventListener("input", resizeInput);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => ask(button.textContent.trim()));
});

messagesElement.addEventListener("click", (event) => {
  const link = event.target.closest("[data-page-id]");
  if (link) openWikiPage(link.dataset.pageId, link.dataset.anchor || "");
});

viewerContent.addEventListener("click", (event) => {
  const link = event.target.closest("[data-page-id]");
  if (link) openWikiPage(link.dataset.pageId, link.dataset.anchor || "");
});

closeViewerButton.addEventListener("click", closeViewer);
viewerResizer.addEventListener("pointerdown", (event) => {
  if (window.matchMedia("(max-width: 640px)").matches) return;
  activeResizePointer = event.pointerId;
  document.body.classList.add("viewer-resizing");
  resizeViewerFromPointer(event.clientX);
  event.preventDefault();
});
document.addEventListener("pointermove", (event) => {
  if (event.pointerId !== activeResizePointer) return;
  resizeViewerFromPointer(event.clientX);
});
document.addEventListener("pointerup", finishViewerResize);
document.addEventListener("pointercancel", finishViewerResize);
viewerResizer.addEventListener("keydown", (event) => {
  const currentWidth = viewer.getBoundingClientRect().width;
  const { min, max } = viewerWidthLimits();
  let nextWidth = currentWidth;
  if (event.key === "ArrowLeft") nextWidth += 24;
  else if (event.key === "ArrowRight") nextWidth -= 24;
  else if (event.key === "Home") nextWidth = min;
  else if (event.key === "End") nextWidth = max;
  else return;
  setViewerWidth(nextWidth);
  event.preventDefault();
});
window.addEventListener("resize", () => {
  if (!viewer.hidden && !window.matchMedia("(max-width: 640px)").matches) {
    setViewerWidth(viewer.getBoundingClientRect().width);
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !viewer.hidden) closeViewer();
});

newChatButton.addEventListener("click", () => {
  const previousSessionId = sessionId;
  sessionId = createSessionId();
  fetch(
    `/api/sessions/${encodeURIComponent(previousSessionId)}/attachments`,
    { method: "DELETE" },
  ).catch(() => {});
  history = [];
  attachments = [];
  renderAttachments();
  setAttachmentStatus();
  messagesElement
    .querySelectorAll(".message")
    .forEach((message) => message.remove());
  if (emptyState) emptyState.hidden = false;
  closeViewer();
  input.value = "";
  resizeInput();
  input.focus();
});

engineSelect.addEventListener("change", updateEngineStatus);

fetch("/api/health")
  .then((response) => response.json())
  .then((health) => {
    healthState = health;
    for (const option of engineSelect.options) {
      const engine = health.engines?.find(
        (candidate) => candidate.id === option.value,
      );
      option.disabled = engine ? !engine.ready : false;
    }
    if (health.ready) {
      const selectedOption = engineSelect.selectedOptions[0];
      if (selectedOption.disabled) {
        const firstReady = health.engines?.find((engine) => engine.ready);
        if (firstReady) engineSelect.value = firstReady.id;
      }
      updateEngineStatus();
      return;
    }
    setStatus(health.wikiError || "Wiki indisponível", "error");
  })
  .catch(() => setStatus("Servidor indisponível", "error"));

resizeInput();
