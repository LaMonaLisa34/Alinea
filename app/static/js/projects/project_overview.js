const projectRead = document.querySelector("#project-read");
const projectEdit = document.querySelector("#project-edit");
const editButton = document.querySelector(".projects__edit");

if (projectRead && projectEdit && editButton) {
  function setEditing(isEditing) {
    projectRead.hidden = isEditing;
    projectEdit.hidden = !isEditing;
    editButton.hidden = isEditing;
  }

  const hasErrors = projectEdit.dataset.hasErrors === "true";
  const editRequested =
    new URLSearchParams(window.location.search).get("mode") === "edit";

  // Conserve l’édition après une erreur ou une demande explicite dans l’URL.
  setEditing(hasErrors || editRequested);

  editButton.addEventListener("click", () => {
    setEditing(true);
    projectEdit.querySelector("#edit-title")?.focus();
  });

  if (hasErrors) {
    projectEdit.querySelector('[aria-invalid="true"]')?.focus();
  }
}

const deleteForm = document.querySelector(".projects__delete-form");
const deleteDialog = document.querySelector(".project-delete-dialog");

if (
  deleteForm &&
  deleteDialog &&
  typeof deleteDialog.showModal === "function"
) {
  const confirmation = deleteForm.querySelector(
    ".projects__delete-confirmation",
  );
  const checkbox = deleteForm.querySelector('[name="confirm_deletion"]');

  if (confirmation && checkbox) {
    // Remplace la case par la fenêtre de confirmation lorsque celle-ci est disponible.
    confirmation.hidden = true;
    checkbox.required = false;
    checkbox.checked = false;

    deleteForm.addEventListener("submit", (event) => {
      // Autorise la soumission après confirmation dans la fenêtre.
      if (checkbox.checked) return;

      event.preventDefault();
      deleteDialog.returnValue = "";
      deleteDialog.showModal();
    });

    deleteDialog.addEventListener("close", () => {
      // Annuler et la touche Échap ferment la fenêtre sans supprimer le projet.
      if (deleteDialog.returnValue !== "confirm") return;

      checkbox.checked = true;
      deleteForm.requestSubmit();
    });

    // Réinitialise la confirmation lors d’un retour sur la page.
    window.addEventListener("pageshow", () => {
      checkbox.checked = false;
    });
  }
}
