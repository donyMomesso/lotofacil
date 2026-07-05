const ADD_BUTTON_SELECTOR = "#colocarnocarrinho";
const CLEAR_BUTTON_SELECTOR = "#limparvolante";
const INCREASE_NUMBER_BUTTON_SELECTOR = "#aumentarnumero";
const NUMBER_CLICK_DELAY_MS = 200;
const NEXT_LINE_DELAY_MS = 1000;
const NUMBER_SELECTOR = [
  "button",
  "a",
  "li",
  "[role='button']",
  "[onclick]",
  "[ng-click]",
  "[data-ng-click]",
  ".numero",
  ".dezena",
  ".number",
  ".ng-binding"
].join(",");
const ADD_BUTTON_TEXTS = [
  "adicionar a lista",
  "adicionar ao carrinho",
  "colocar no carrinho",
  "incluir aposta"
];

let isRunning = false;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeText(text) {
  return String(text || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

function isVisible(element) {
  const rect = element.getBoundingClientRect();
  const style = window.getComputedStyle(element);

  return rect.width > 0
    && rect.height > 0
    && style.visibility !== "hidden"
    && style.display !== "none";
}

function isDisabled(element) {
  return element.disabled
    || element.getAttribute("aria-disabled") === "true"
    || element.classList.contains("disabled");
}

function getClickableAncestor(element) {
  return element.closest("button, a, li, [role='button'], [onclick], [ng-click], [data-ng-click], .numero, .dezena, .number")
    || element;
}

function getNumberCandidates() {
  const directCandidates = Array.from(document.querySelectorAll(NUMBER_SELECTOR));
  const exactTextCandidates = Array.from(document.querySelectorAll("body *"))
    .filter((element) => /^\d{2}$/.test(normalizeText(element.innerText || element.textContent)));

  return Array.from(new Set([...directCandidates, ...exactTextCandidates]));
}

function findNumberElement(number) {
  const normalizedNumber = normalizeText(number);
  const numberById = document.getElementById(`n${normalizedNumber}`);

  if (numberById && isVisible(numberById) && !isDisabled(numberById)) {
    return getClickableAncestor(numberById);
  }

  const match = getNumberCandidates().find((element) => {
    const text = normalizeText(element.innerText || element.textContent);
    return text === normalizedNumber && isVisible(element) && !isDisabled(element);
  });

  return match ? getClickableAncestor(match) : null;
}

function findClearButton() {
  return document.querySelector(CLEAR_BUTTON_SELECTOR);
}

function findIncreaseNumberButton() {
  return document.querySelector(INCREASE_NUMBER_BUTTON_SELECTOR);
}

function findAddButton() {
  const buttonBySelector = document.querySelector(ADD_BUTTON_SELECTOR);

  if (buttonBySelector) {
    return buttonBySelector;
  }

  const candidates = Array.from(document.querySelectorAll("button, a, input[type='button'], input[type='submit']"));

  return candidates.find((element) => {
    const text = normalizeText(element.innerText || element.value).toLowerCase();
    return ADD_BUTTON_TEXTS.some((label) => text.includes(label));
  });
}

function dispatchRealClick(element) {
  const rect = element.getBoundingClientRect();
  const clientX = rect.left + rect.width / 2;
  const clientY = rect.top + rect.height / 2;
  const eventOptions = {
    bubbles: true,
    cancelable: true,
    view: window,
    clientX,
    clientY
  };

  element.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
  element.dispatchEvent(new PointerEvent("pointerdown", eventOptions));
  element.dispatchEvent(new MouseEvent("mousedown", eventOptions));
  element.dispatchEvent(new PointerEvent("pointerup", eventOptions));
  element.dispatchEvent(new MouseEvent("mouseup", eventOptions));
  element.dispatchEvent(new MouseEvent("click", eventOptions));
}

async function clickNumber(number) {
  const element = findNumberElement(number);

  if (!element) {
    console.warn(`[Preenchedor] Numero nao encontrado no DOM: ${number}`);
    return false;
  }

  dispatchRealClick(element);
  await sleep(NUMBER_CLICK_DELAY_MS);
  return true;
}

async function clearVolante() {
  const clearButton = findClearButton();

  if (!clearButton) {
    console.warn(`[Preenchedor] Botao limpar volante nao encontrado: ${CLEAR_BUTTON_SELECTOR}`);
    return;
  }

  dispatchRealClick(clearButton);
  await sleep(NUMBER_CLICK_DELAY_MS);
}

async function adjustNumberQuantity(line) {
  const extraNumbers = Math.max(0, line.length - 15);

  if (!extraNumbers) {
    return;
  }

  const increaseButton = findIncreaseNumberButton();

  if (!increaseButton) {
    throw new Error(`Jogo com ${line.length} dezenas, mas nao encontrei o botao de aumentar numeros: ${INCREASE_NUMBER_BUTTON_SELECTOR}`);
  }

  for (let index = 0; index < extraNumbers; index += 1) {
    dispatchRealClick(increaseButton);
    await sleep(NUMBER_CLICK_DELAY_MS);
  }
}

async function clickAddButton() {
  const addButton = findAddButton();

  if (!addButton) {
    throw new Error(`Botao de adicionar nao encontrado: ${ADD_BUTTON_SELECTOR}`);
  }

  dispatchRealClick(addButton);
}

async function processLine(line, lineIndex) {
  console.info(`[Preenchedor] Processando linha ${lineIndex + 1}:`, line);

  const notClicked = [];

  await clearVolante();
  await adjustNumberQuantity(line);

  for (const number of line) {
    const clicked = await clickNumber(number);

    if (!clicked) {
      notClicked.push(number);
    }
  }

  if (notClicked.length) {
    throw new Error(`Linha ${lineIndex + 1}: nao encontrei/click nos numeros ${notClicked.join(", ")}.`);
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

  sendResponse({
    ok: true,
    message: "Preenchimento iniciado. Acompanhe na pagina da Caixa."
  });

  processLines(message.lines)
    .catch((error) => {
      console.error("[Preenchedor] Erro:", error);
    });

  return false;
});
