const form = document.querySelector("#analyze-form");
const fileInput = document.querySelector("#image");
const preview = document.querySelector("#preview");
const statusNode = document.querySelector("#status");
const analysisNode = document.querySelector("#analysis");
const modelIdNode = document.querySelector("#model-id");
const predictionsNode = document.querySelector("#predictions");
const submitButton = form.querySelector("button");

fileInput.addEventListener("change", () => {
  const [file] = fileInput.files;
  if (!file) {
    preview.hidden = true;
    preview.removeAttribute("src");
    return;
  }

  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const [file] = fileInput.files;
  if (!file) {
    statusNode.textContent = "Choose an image first.";
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
