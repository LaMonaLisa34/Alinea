const preview = document.querySelector("#home-preview");
const controls = document.querySelector(".home-showcase__controls");

if (preview && controls) {
  // L’indice de chaque exemple correspond à l’attribut data-example du bouton.
  const examples = [
    {
      title: "Le Frison",
      sections: ["Introduction", "Morphologie", "Taille", "Robes", "Histoire", "Sources"],
      text: "Le Frison est une race de cheval originaire de Frise, aux Pays-Bas. Il est notamment connu pour sa robe noire et sa silhouette expressive.",
      sources: ["Royal Friesian Studbook (KFPS)", "Wikipédia : Frison"],
    },
    {
      title: "Sac à dos de randonnée",
      sections: ["Présentation", "Capacité", "Matériaux", "Dimensions", "Entretien", "Sources"],
      text: "Ce sac de 25 litres est conçu pour les sorties à la journée. Ses poches latérales gardent les gourdes accessibles, et sa sangle pectorale stabilise le portage.",
      sources: ["Fiche fournisseur", "Notice d’entretien"],
    },
    {
      title: "Guide du compostage",
      sections: ["Introduction", "Matériel", "Bons gestes", "Erreurs", "FAQ", "Sources"],
      text: "Pour démarrer un compost, alternez les déchets de cuisine et les matières sèches. Gardez le mélange humide et aérez-le régulièrement.",
      sources: ["Notes éditoriales", "Guide de compostage"],
    },
    {
      title: "Vélo de ville d’occasion",
      sections: ["Description", "Caractéristiques", "État", "Prix", "Remise", "Sources"],
      text: "Vélo de ville à 7 vitesses, équipé d’un porte-bagages et de garde-boue. Quelques rayures sur le cadre. Prix : 120 €. À récupérer sur place.",
      sources: ["Photos de l’article", "Informations du vendeur"],
    },
    {
      title: "Installer Alinea en local",
      sections: ["Prérequis", "Configuration", "Démarrage", "Vérification", "Dépannage", "Sources"],
      text: "Avant de démarrer, installez Docker avec Compose et récupérez le dépôt Alinea. Préparez ensuite la configuration locale en suivant les instructions du README.",
      sources: ["README du projet", "Configuration Docker Compose"],
    },
  ];

  const title = preview.querySelector(".home-preview__header strong");
  const heading = preview.querySelector(".home-preview__content h2");
  const text = preview.querySelector(".home-preview__content > p");
  const sections = preview.querySelectorAll(".home-preview__outline li");
  const sources = preview.querySelectorAll("[data-preview-source]");
  const buttons = controls.querySelectorAll("button[data-example]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  let current = 0;
  let animation;

  function showExample(index) {
    const example = examples[index];

    if (!example || index === current) return;

    current = index;
    title.textContent = example.title;
    heading.textContent = example.sections[0];
    text.textContent = example.text;

    sections.forEach((section, position) => {
      section.textContent = example.sections[position];
    });

    // Met à jour uniquement les libellés pour conserver les icônes des sources.
    sources.forEach((source, position) => {
      source.textContent = example.sources[position];
    });

    buttons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        String(Number(button.dataset.example) === current),
      );
    });

    // Annule la transition précédente si les sélections se succèdent rapidement.
    animation?.cancel();

    if (!reducedMotion.matches) {
      animation = preview.animate(
        [
          { opacity: 0.55, transform: "translateY(5px)" },
          { opacity: 1, transform: "translateY(0)" },
        ],
        { duration: 260, easing: "ease-out" },
      );
    }
  }

  const showcase = preview.closest(".home-showcase") ?? preview;
  const rotationDelay = 2000;

  let timer;
  let manuallySelected = false;

  function stopRotation() {
    window.clearTimeout(timer);
  }

  function scheduleRotation() {
    // Annule le délai précédent pour ne garder qu’un seul changement programmé.
    stopRotation();

    // Suspend le défilement pendant la consultation de l’aperçu
    // et respecte la préférence de réduction des animations.
    if (
      manuallySelected ||
      reducedMotion.matches ||
      document.hidden ||
      showcase.matches(":hover, :focus-within")
    ) {
      return;
    }

    timer = window.setTimeout(() => {
      showExample((current + 1) % examples.length);
      scheduleRotation();
    }, rotationDelay);
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      // Le choix manuel prend la main sur le défilement automatique.
      manuallySelected = true;
      stopRotation();
      showExample(Number(button.dataset.example));
    });
  });

  showcase.addEventListener("mouseenter", stopRotation);
  showcase.addEventListener("mouseleave", scheduleRotation);
  showcase.addEventListener("focusin", stopRotation);
  showcase.addEventListener("focusout", () => {
    // Attend le déplacement du focus avant de vérifier s’il a quitté l’aperçu.
    window.requestAnimationFrame(scheduleRotation);
  });

  document.addEventListener("visibilitychange", scheduleRotation);
  reducedMotion.addEventListener("change", scheduleRotation);

  // Affiche les boutons une fois leurs interactions prêtes.
  controls.hidden = false;
  scheduleRotation();
}
