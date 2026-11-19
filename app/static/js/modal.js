// Gestion des modales personnalisées
document.addEventListener('DOMContentLoaded', () => {
  // Ouvrir une modale
  document.addEventListener('click', (e) => {
    const button = e.target.closest('[data-modal]');
    if (!button) return;

    const modalId = button.dataset.modal;
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.showModal();
  });

  // Fermer une modale
  document.addEventListener('click', (e) => {
    const closeButton = e.target.closest('.modal__close');
    if (!closeButton) return;

    const modal = closeButton.closest('.modal');
    if (modal) {
      modal.close();
    }
  });

  // Annuler (bouton Annuler)
  document.addEventListener('click', (e) => {
    const cancelButton = e.target.closest('[data-action="cancel"]');
    if (!cancelButton) return;

    const modal = cancelButton.closest('.modal');
    if (modal) {
      modal.close();
    }
  });

  // Fermer en cliquant sur l'overlay
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal__overlay')) {
      const modal = e.target.closest('.modal');
      if (modal) {
        modal.close();
      }
    }
  });

  // Fermer avec Échap
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const openModals = document.querySelectorAll('.modal[open]');
      openModals.forEach(modal => modal.close());
    }
  });
});
