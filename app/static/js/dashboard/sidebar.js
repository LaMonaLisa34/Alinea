/**
 * Gestion du menu burger et de la sidebar mobile
 */
document.addEventListener('DOMContentLoaded', function() {
  const toggleButton = document.getElementById('dashboard-menu-toggle');
  const sidebar = document.getElementById('dashboard-menu');

  if (!toggleButton || !sidebar) return;

  // Basculer le menu
  toggleButton.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    const isOpen = sidebar.hasAttribute('open');
    
    if (isOpen) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  // Fermer le menu en cliquant sur un lien
  const links = sidebar.querySelectorAll('a');
  links.forEach(link => {
    link.addEventListener('click', function() {
      closeSidebar();
    });
  });

  // Fermer le menu en cliquant en dehors (overlay ou ailleurs)
  document.addEventListener('click', function(e) {
    // Vérifier si on est sur mobile
    if (window.innerWidth > 800) return;
    
    const isClickInsideSidebar = sidebar.contains(e.target);
    const isClickOnToggle = toggleButton.contains(e.target);
    
    if (!isClickInsideSidebar && !isClickOnToggle && sidebar.hasAttribute('open')) {
      closeSidebar();
    }
  });

  function openSidebar() {
    sidebar.setAttribute('open', '');
    toggleButton.setAttribute('aria-expanded', 'true');
    toggleButton.setAttribute('aria-label', 'Fermer le menu');
  }

  function closeSidebar() {
    sidebar.removeAttribute('open');
    toggleButton.setAttribute('aria-expanded', 'false');
    toggleButton.setAttribute('aria-label', 'Ouvrir le menu');
  }
});
