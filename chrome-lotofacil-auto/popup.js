const inputEl = document.getElementById("numbersInput");
const startButton = document.getElementById("startButton");
const statusEl = document.getElementById("status");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function parseLines(rawText) {
  return rawText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const numbers = line.match(/\d{2}/g) || [];
      return numbers;
    })
    .filter((numbers) => numbers.length > 0);
}

async function getActiveTab() {
  if (!chrome?.tabs?.query) {
    throw new Error("Abra este popup pelo icone da extensao, nao diretamente como arquivo HTML.");
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function ensureContentScript(tabId) {
  if (!chrome?.scripting?.executeScript) {
    throw new Error("API chrome.scripting indisponivel. Recarregue a extensao em chrome://extensions.");
  }

  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"]
  });
}

async function sendLinesToContentScript(tabId, lines) {
  return chrome.tabs.sendMessage(tabId, {
    type: "START_FILLING_NUMBERS",
    lines
  });
}

startButton.addEventListener("click", async () => {
  const lines = parseLines(inputEl.value);

  if (!lines.length) {
    setStatus("Cole pelo menos uma linha de numeros.", true);
    return;
  }

  startButton.disabled = true;
  setStatus("Enviando dados para a pagina ativa...");

  try {
    const tab = await getActiveTab();

    if (!tab?.id) {
      throw new Error("Nao foi possivel encontrar a aba ativa.");
    }

    await ensureContentScript(tab.id);
    const response = await sendLinesToContentScript(tab.id, lines);

    setStatus(response?.message || "Preenchimento iniciado.");
  } catch (error) {
    setStatus(error.message || "Falha ao iniciar preenchimento.", true);
  } finally {
    startButton.disabled = false;
  }
});
