const mobileMenu = document.querySelector(".site-header__mobile");

if (mobileMenu) {
  const toggle = mobileMenu.querySelector("summary");

  // Échap ferme le menu et rend le focus au bouton d’ouverture.
  mobileMenu.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && mobileMenu.open) {
      mobileMenu.open = false;
      toggle?.focus();
    }
  });

  // Ferme le menu après un clic sur un lien ou en dehors du menu.
  document.addEventListener("click", (event) => {
    if (!mobileMenu.open || !(event.target instanceof Element)) return;

    if (
      !mobileMenu.contains(event.target) ||
      event.target.closest(".site-header__panel a")
    ) {
      mobileMenu.open = false;
    }
  });
}
