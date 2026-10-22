// Interações progressivas: cadastros e consultas também funcionam sem JavaScript.
const toggle = document.querySelector('.menu-toggle');
const sidebar = document.querySelector('.sidebar');
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  sidebar.classList.toggle('is-open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    sidebar.classList.remove('is-open');
    toggle?.setAttribute('aria-expanded', 'false');
    toggle?.setAttribute('aria-label', 'Abrir menu');
  }
});
document.querySelector('#report-select')?.addEventListener('change', event => {
  const destination = new URL(window.location.href);
  destination.search = new URLSearchParams({report: event.target.value});
  window.location.assign(destination);
});
