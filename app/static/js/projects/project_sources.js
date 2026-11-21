const deleteDialog = document.querySelector(".source-delete-dialog");

if (deleteDialog && typeof deleteDialog.showModal === "function") {
  let pendingForm = null;

  document.querySelectorAll(".project-sources__delete-form").forEach((form) => {
    const confirmation = form.querySelector(".project-sources__confirmation");
    const checkbox = form.querySelector('[name="confirm_deletion"]');

    if (!confirmation || !checkbox) return;

    // La fenêtre remplace la case de confirmation lorsque JavaScript est actif.
    confirmation.hidden = true;
    checkbox.required = false;
    checkbox.checked = false;

    form.addEventListener("submit", (event) => {
      // Autorise l’envoi uniquement après confirmation dans la fenêtre.
      if (checkbox.checked) return;

      event.preventDefault();
      pendingForm = form;
      deleteDialog.returnValue = "";
      deleteDialog.showModal();
    });
  });

  deleteDialog.addEventListener("close", () => {
    const form = pendingForm;
    pendingForm = null;

    if (!form) return;

    // Annuler et la touche Échap ferment la fenêtre sans supprimer la source.
    if (deleteDialog.returnValue !== "confirm") return;

    const checkbox = form.querySelector('[name="confirm_deletion"]');
    checkbox.checked = true;

    // Conserve la soumission POST, le jeton CSRF et la validation du formulaire.
    form.requestSubmit();
  });
}

document.querySelectorAll("[data-source-form]").forEach((form) => {
  const sourceType = form.querySelector('[name="source_type"]');
  const urlGroup = form.querySelector("[data-source-url]");
  const textGroup = form.querySelector("[data-source-text]");

  if (!sourceType || !urlGroup || !textGroup) return;

  const urlInput = urlGroup.querySelector("input");
  const textInput = textGroup.querySelector("textarea");

  if (!urlInput || !textInput) return;

  function updateSourceFields() {
    const isUrl = sourceType.value === "url";
    const isText = sourceType.value === "text";

    // Affiche et soumet uniquement le contenu correspondant au type choisi.
    urlGroup.hidden = !isUrl;
    urlInput.disabled = !isUrl;
    urlInput.required = isUrl;

    textGroup.hidden = !isText;
    textInput.disabled = !isText;
    textInput.required = isText;
  }

  sourceType.addEventListener("change", updateSourceFields);
  updateSourceFields();
});
