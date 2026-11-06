const projectRead = document.querySelector("#project-read");
const projectEdit = document.querySelector("#project-edit");
const editButton = document.querySelector(".projects__edit");

if (projectRead && projectEdit && editButton) {
  function setEditing(isEditing) {
    projectRead.hidden = isEditing;
    projectEdit.hidden = !isEditing;
    editButton.hidden = isEditing;
  }

  // Conserve le formulaire ouvert lorsque la validation serveur a échoué.
  const hasErrors = projectEdit.dataset.hasErrors === "true";
  setEditing(hasErrors);

  editButton.addEventListener("click", () => {
    setEditing(true);

    // Place le focus au début du formulaire pour la navigation au clavier.
    projectEdit.querySelector("#edit-title")?.focus();
  });

  if (hasErrors) {
    // Dirige l’utilisateur vers le premier champ signalé comme invalide.
    projectEdit.querySelector('[aria-invalid="true"]')?.focus();
  }
}
