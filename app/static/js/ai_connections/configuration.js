const configurationForm = document.querySelector(".ai-configuration__form");

if (configurationForm) {
  const submitButton = configurationForm.querySelector(
    ".ai-configuration__submit",
  );
  const submitLabel = configurationForm.querySelector("[data-submit-label]");
  const spinner = configurationForm.querySelector(
    ".ai-configuration__spinner",
  );
  const progress = configurationForm.querySelector(
    ".ai-configuration__progress",
  );
  const mode = configurationForm.querySelector('[name="mode"]');

  let submitting = false;

  function resetSubmission() {
    submitting = false;
    configurationForm.removeAttribute("aria-busy");
    submitButton.disabled = false;
    submitLabel.textContent = "Enregistrer et tester";
    spinner.hidden = true;
    progress.textContent = "";
  }

  configurationForm.addEventListener("submit", (event) => {
    // Empêche les doubles soumissions pendant l’attente de la réponse.
    if (submitting) {
      event.preventDefault();
      return;
    }

    submitting = true;
    configurationForm.setAttribute("aria-busy", "true");
    submitButton.disabled = true;
    submitLabel.textContent = "Traitement en cours…";
    spinner.hidden = false;

    progress.textContent =
      mode?.value === "ollama"
        ? "Enregistrement et test du modèle en cours…"
        : "Enregistrement de la configuration en cours…";
  });

  // Restaure le bouton lorsque le navigateur réaffiche une page mise en cache.
  window.addEventListener("pageshow", resetSubmission);
}
