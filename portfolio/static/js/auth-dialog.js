(() => {
  const dialog = document.querySelector('#auth-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const slot = dialog.querySelector('#auth-form-slot');
  const error = dialog.querySelector('.auth-network-error');
  const tabs = [...dialog.querySelectorAll('[data-auth-mode]')];
  let controller, opener, destination = '', mode = 'login', submitting = false;
  const showError = message => { error.textContent = message; error.hidden = false; };
  const focusForm = () => {
    (slot.querySelector('.error-summary') || slot.querySelector('input:not([type=hidden])'))?.focus({preventScroll: true});
  };
  const load = async selected => {
    controller?.abort();
    controller = new AbortController();
    mode = selected;
    tabs.forEach(tab => tab.setAttribute('aria-pressed', String(tab.dataset.authMode === mode)));
    error.hidden = true;
    slot.setAttribute('aria-busy', 'true');
    slot.innerHTML = '<p class="auth-loading">Preparando tu espacio…</p>';
    const url = new URL(mode === 'register' ? dialog.dataset.registerUrl : dialog.dataset.loginUrl, location.origin);
    if (destination) url.searchParams.set('next', destination);
    try {
      const response = await fetch(url, {headers: {'X-Oniria-Modal': '1'}, credentials: 'same-origin', signal: controller.signal});
      if (!response.ok) throw new Error('load');
      if (response.redirected) { location.assign(response.url); return; }
      slot.innerHTML = await response.text();
      slot.removeAttribute('aria-busy');
      focusForm();
    } catch (err) {
      if (err.name === 'AbortError') return;
      slot.removeAttribute('aria-busy');
      slot.innerHTML = '';
      showError('No pudimos cargar el formulario. Vuelve a seleccionar Ingresar o Crear cuenta para reintentar.');
    }
  };
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href, location.origin);
    if (url.origin !== location.origin || ![dialog.dataset.loginUrl, dialog.dataset.registerUrl].includes(url.pathname)) return;
    event.preventDefault();
    opener = link;
    destination = url.searchParams.get('next') || '';
    document.querySelector('.site-header')?.classList.remove('menu-open');
    document.querySelector('.nav-toggle')?.setAttribute('aria-expanded', 'false');
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('auth-is-open');
    load(url.pathname === dialog.dataset.registerUrl ? 'register' : 'login');
  });
  tabs.forEach(tab => tab.addEventListener('click', () => { if (!submitting) load(tab.dataset.authMode); }));
  dialog.querySelector('.auth-close').addEventListener('click', () => { if (!submitting) dialog.close(); });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog || submitting) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('cancel', event => { if (submitting) event.preventDefault(); });
  dialog.addEventListener('close', () => {
    controller?.abort();
    document.body.classList.remove('auth-is-open');
    const returnTo = opener?.getClientRects().length ? opener : document.querySelector('.nav-toggle');
    returnTo?.focus({preventScroll: true});
    slot.innerHTML = '';
  });
  slot.addEventListener('submit', async event => {
    const form = event.target.closest('form');
    if (!form || submitting) return;
    event.preventDefault();
    submitting = true;
    error.hidden = true;
    const button = form.querySelector('[type=submit]');
    button.disabled = true;
    tabs.forEach(tab => { tab.disabled = true; });
    form.setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(form.action, {method: 'POST', body: new FormData(form), headers: {'X-Oniria-Modal': '1'}, credentials: 'same-origin'});
      if (!response.ok) throw new Error('submit');
      if (response.headers.get('content-type')?.includes('application/json')) {
        const result = await response.json();
        location.assign(result.redirect);
        return;
      }
      if (response.redirected) { location.assign(response.url); return; }
      slot.innerHTML = await response.text();
      focusForm();
    } catch {
      showError('No pudimos completar la solicitud. Revisa tu conexión e inténtalo de nuevo.');
      button.disabled = false;
    } finally {
      submitting = false;
      tabs.forEach(tab => { tab.disabled = false; });
      form.removeAttribute('aria-busy');
    }
  });
})();
