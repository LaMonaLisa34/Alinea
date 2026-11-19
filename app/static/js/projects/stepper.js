// Gestion de la barre d'étapes (stepper)
document.addEventListener('DOMContentLoaded', () => {
  const stepper = document.querySelector('.stepper');
  if (!stepper) return;

  const items = document.querySelectorAll('.stepper__item');
  const prevBtn = document.querySelector('.stepper__button--prev');
  const nextBtn = document.querySelector('.stepper__button--next');

  let currentStep = 0;

  // Mettre à jour l'affichage des boutons
  const updateButtons = () => {
    prevBtn.disabled = currentStep === 0;
    nextBtn.disabled = currentStep === items.length - 1;
  };

  // Changer l'étape active
  const goToStep = (step) => {
    if (step < 0 || step >= items.length) return;

    // Retirer la classe active de toutes les étapes
    items.forEach(item => item.classList.remove('stepper__item--active'));

    // Ajouter la classe active à l'étape actuelle
    items[step].classList.add('stepper__item--active');

    // Marquer toutes les étapes antérieures comme complétées
    for (let i = 0; i < step; i++) {
      items[i].classList.add('stepper__item--completed');
    }

    // Retirer la classe complétée des étapes suivantes
    for (let i = step + 1; i < items.length; i++) {
      items[i].classList.remove('stepper__item--completed');
    }

    currentStep = step;
    updateButtons();
  };

  // Bouton précédent
  prevBtn.addEventListener('click', () => {
    goToStep(currentStep - 1);
  });

  // Bouton suivant
  nextBtn.addEventListener('click', () => {
    goToStep(currentStep + 1);
  });

  // Cliquer sur une étape
  items.forEach((item, index) => {
    item.addEventListener('click', () => {
      // Permettre de cliquer que sur les étapes antérieures
      if (index <= currentStep) {
        goToStep(index);
      }
    });

    // Ajouter le curseur sur les étapes antérieures
    if (index <= currentStep) {
      item.style.cursor = 'pointer';
    }
  });

  // Initialiser
  updateButtons();
});
