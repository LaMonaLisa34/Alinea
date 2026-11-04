(() => {
  // Apparition des blocs au défilement.
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!reducedMotion.matches && "IntersectionObserver" in window) {
    const targets = document.querySelectorAll(
      ".home__step, .home__use-cases-heading, .home__section-description, .home__card",
    );

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.15 },
    );

    targets.forEach((target) => {
      target.classList.add("home-reveal");
      observer.observe(target);
    });
  }

  // Inclinaison de l’aperçu selon la position de la souris.
  const showcase = document.querySelector(".home-showcase");
  const preview = document.querySelector("#home-preview");
  const canHover = window.matchMedia("(hover: hover)");

  if (showcase && preview && canHover.matches && !reducedMotion.matches) {
    const maxTilt = 3;

    showcase.addEventListener("mousemove", (event) => {
      const rect = showcase.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;

      preview.style.transform =
        `perspective(1000px) rotateX(${-y * maxTilt}deg) rotateY(${x * maxTilt}deg)`;
    });

    showcase.addEventListener("mouseleave", () => {
      preview.style.transform = "";
    });
  }
})();
