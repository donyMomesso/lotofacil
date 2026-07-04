const ADD_BUTTON_SELECTOR = "#botao-adicionar";
const NUMBER_CLICK_DELAY_MS = 200;
const NEXT_LINE_DELAY_MS = 1000;

let isRunning = false;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeText(text) {
  return String(text || "").trim();
}

function getClickableCandidates() {
  return Array.from(document.querySelectorAll("li, a, button"));
}

function findNumberElement(number) {
  const normalizedNumber = normalizeText(number);

  return getClickableCandidates().find((element) => {
    return normalizeText(element.innerText) === normalizedNumber;
  });
}

function findAddButton() {
  return document.querySelector(ADD_BUTTON_SELECTOR);
}

async function clickNumber(number) {
  const element = findNumberElement(number);

  if (!element) {
    console.warn(`[Preenchedor] Numero nao encontrado no DOM: ${number}`);
    return false;
  }

  element.click();
  await sleep(NUMBER_CLICK_DELAY_MS);
  return true;
}

async function clickAddButton() {
  const addButton = findAddButton();

  if (!addButton) {
    throw new Error(`Botao de adicionar nao encontrado: ${ADD_BUTTON_SELECTOR}`);
  }

  addButton.click();
}

async function processLine(line, lineIndex) {
  console.info(`[Preenchedor] Processando linha ${lineIndex + 1}:`, line);

  for (const number of line) {
    await clickNumber(number);
  }

  await clickAddButton();
  await sleep(NEXT_LINE_DELAY_MS);
}

async function processLines(lines) {
  if (isRunning) {
    throw new Error("Ja existe um preenchimento em execucao.");
  }

  isRunning = true;

  try {
    for (let index = 0; index < lines.length; index += 1) {
      await processLine(lines[index], index);
    }

    console.info("[Preenchedor] Preenchimento finalizado.");
  } finally {
    isRunning = false;
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "START_FILLING_NUMBERS") {
    return false;
  }

  processLines(message.lines)
    .then(() => {
      sendResponse({
        ok: true,
        message: "Preenchimento finalizado."
      });
    })
    .catch((error) => {
      console.error("[Preenchedor] Erro:", error);
      sendResponse({
        ok: false,
        message: error.message || "Erro durante o preenchimento."
      });
    });

  return true;
});
