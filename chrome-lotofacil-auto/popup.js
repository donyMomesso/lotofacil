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

function runFillingInPage(lines) {
  const ADD_BUTTON_ID = "colocarnocarrinho";
  const CLEAR_BUTTON_ID = "limparvolante";
  const INCREASE_NUMBER_BUTTON_ID = "aumentarnumero";
  const NUMBER_CLICK_DELAY_MS = 220;
  const NEXT_LINE_DELAY_MS = 1200;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function clickById(id) {
    const element = document.getElementById(id);

    if (!element) {
      console.warn(`[Preenchedor] Elemento nao encontrado: #${id}`);
      return false;
    }

    element.click();
    return true;
  }

  async function clearVolante() {
    clickById(CLEAR_BUTTON_ID);
    await sleep(NUMBER_CLICK_DELAY_MS);
  }

  async function adjustNumberQuantity(line) {
    const extraNumbers = Math.max(0, line.length - 15);

    for (let index = 0; index < extraNumbers; index += 1) {
      clickById(INCREASE_NUMBER_BUTTON_ID);
      await sleep(NUMBER_CLICK_DELAY_MS);
    }
  }

  async function clickNumbers(line) {
    const missing = [];

    for (const number of line) {
      const clicked = clickById(`n${number}`);

      if (!clicked) {
        missing.push(number);
      }

      await sleep(NUMBER_CLICK_DELAY_MS);
    }

    if (missing.length) {
      throw new Error(`Nao encontrei as dezenas: ${missing.join(", ")}`);
    }
  }

  async function processLine(line, index) {
    console.info(`[Preenchedor] Linha ${index + 1}`, line);

    await clearVolante();
    await adjustNumberQuantity(line);
    await clickNumbers(line);
    await sleep(300);
    clickById(ADD_BUTTON_ID);
    await sleep(NEXT_LINE_DELAY_MS);
  }

  async function start() {
    if (window.__preenchedorDeDezenasRodando) {
      console.warn("[Preenchedor] Ja existe um preenchimento em execucao.");
      return;
    }

    window.__preenchedorDeDezenasRodando = true;

    try {
      for (let index = 0; index < lines.length; index += 1) {
        await processLine(lines[index], index);
      }

      console.info("[Preenchedor] Preenchimento finalizado.");
    } catch (error) {
      console.error("[Preenchedor] Erro:", error);
      alert(`Preenchedor de Dezenas: ${error.message}`);
    } finally {
      window.__preenchedorDeDezenasRodando = false;
    }
  }

  start();
  return true;
}

async function startFillingOnActiveTab(tabId, lines) {
  if (!chrome?.scripting?.executeScript) {
    throw new Error("API chrome.scripting indisponivel. Recarregue a extensao em chrome://extensions.");
  }

  return chrome.scripting.executeScript({
    target: { tabId },
    func: runFillingInPage,
    args: [lines]
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

    await startFillingOnActiveTab(tab.id, lines);
    setStatus("Preenchimento iniciado na pagina da Caixa.");
  } catch (error) {
    setStatus(error.message || "Falha ao iniciar preenchimento.", true);
  } finally {
    startButton.disabled = false;
  }
});
