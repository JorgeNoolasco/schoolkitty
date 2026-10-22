const COOKIE = 'school_session';
async function verify(token, secret) {
  try {
    const [encoded, signature] = token.split('.');
    const decode = value => Uint8Array.from(atob(value.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
    const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
    if (!await crypto.subtle.verify('HMAC', key, decode(signature), new TextEncoder().encode(encoded))) return false;
    const payload = JSON.parse(new TextDecoder().decode(decode(encoded)));
    return payload.exp > Date.now() && payload.sub === process.env.ADMIN_USERNAME;
  } catch { return false; }
}
export default async function middleware(request) {
  const url = new URL(request.url);
  if (url.pathname === '/painel.html') {
    const cookie = request.headers.get('cookie') || '';
    const token = cookie.split(';').map(part => part.trim()).find(part => part.startsWith(`${COOKIE}=`))?.slice(COOKIE.length + 1);
    if (!process.env.SESSION_SECRET || new TextEncoder().encode(process.env.SESSION_SECRET).length < 32 || !token || !await verify(token, process.env.SESSION_SECRET)) return Response.redirect(new URL('/login.html', request.url), 307);
  }
  return;
}
export const config = { matcher: ['/painel', '/painel.html'] };
