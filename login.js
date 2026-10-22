document.querySelector('#loginForm').addEventListener('submit', async event => {
  event.preventDefault(); const form = event.currentTarget, message = document.querySelector('#loginMessage');
  message.className = 'auth-message'; message.textContent = 'Verificando acesso…';
  try {
    const response = await fetch('/api/auth-login', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ username: form.username.value.trim(), password: form.password.value }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Não foi possível entrar.');
    location.assign('/painel.html');
  } catch (error) { message.textContent = error.message === 'Failed to fetch' ? 'Não foi possível conectar ao servidor.' : error.message; }
});
