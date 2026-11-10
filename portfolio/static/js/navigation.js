const header = document.querySelector('.site-header');
const toggle = header?.querySelector('.nav-toggle');
if (toggle) {
  const closeMenu = () => {
    toggle.setAttribute('aria-expanded', 'false');
    header.classList.remove('menu-open');
  };
  header.dataset.menuReady = 'true';
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    header.classList.toggle('menu-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && header.classList.contains('menu-open')) {
      closeMenu();
      toggle.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target)) closeMenu();
  });
  window.matchMedia('(max-width: 700px)').addEventListener('change', closeMenu);
}
