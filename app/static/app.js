const form = document.querySelector("#analyze-form");
const fileInput = document.querySelector("#image");
const pasteZone = document.querySelector("#paste-zone");
const preview = document.querySelector("#preview");
const statusNode = document.querySelector("#status");
const analysisNode = document.querySelector("#analysis");
const modelIdNode = document.querySelector("#model-id");
const predictionsNode = document.querySelector("#predictions");
const submitButton = form.querySelector("button");
let pendingFile = null;

fileInput.addEventListener("change", () => {
  const [file] = fileInput.files;
  if (!file) {
    pendingFile = null;
    preview.hidden = true;
    preview.removeAttribute("src");
    return;
  }

  pendingFile = file;
  renderPreview(file);
});

pasteZone.addEventListener("click", () => {
  pasteZone.focus();
});

pasteZone.addEventListener("paste", (event) => {
  const file = extractImageFromClipboard(event.clipboardData);
  if (!file) {
    statusNode.textContent = "Clipboard does not contain an image.";
    return;
  }

  event.preventDefault();
  pendingFile = file;
  fileInput.value = "";
  renderPreview(file);
  statusNode.textContent = "Clipboard image ready for analysis.";
});

pasteZone.addEventListener("focus", () => {
  pasteZone.classList.add("is-active");
});

pasteZone.addEventListener("blur", () => {
  pasteZone.classList.remove("is-active");
});

function extractImageFromClipboard(clipboardData) {
  if (!clipboardData) {
    return null;
  }

  for (const item of clipboardData.items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) {
        return new File([file], file.name || "pasted-image.png", {
          type: file.type || "image/png",
        });
      }
    }
  }

  return null;
}

function renderPreview(file) {
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = pendingFile || fileInput.files[0];
  if (!file) {
    statusNode.textContent = "Choose or paste an image first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  submitButton.disabled = true;
  analysisNode.hidden = true;
  statusNode.textContent = "Running plant species identification. The first request will be slower while the model loads.";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.detail || "Analysis failed.");
    }

    const result = await response.json();
    modelIdNode.textContent = result.model_id;
    predictionsNode.replaceChildren(
      ...result.predictions.map((prediction) => {
        const item = document.createElement("li");
        item.textContent = `${prediction.label}: ${(prediction.confidence * 100).toFixed(2)}%`;
        return item;
      }),
    );
    analysisNode.hidden = false;
    statusNode.textContent = `Returned ${result.predictions.length} candidate species.`;
  } catch (error) {
    statusNode.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
