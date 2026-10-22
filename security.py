"""Proteção de formulários e sessões locais, sem autenticação adicional."""
import secrets


def csrf_token(request):
    if 'csrf' not in request.session:
        request.session['csrf'] = secrets.token_hex(32)
    return request.session['csrf']


def valid_csrf(request, value):
    expected = request.session.get('csrf')
    return (isinstance(value, str) and isinstance(expected, str)
            and value.isascii() and secrets.compare_digest(value, expected))
