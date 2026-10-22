"""Verificação opcional no Chrome local; requer o pacote Python playwright."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://127.0.0.1:8000'
output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.tools/screenshots')
output.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width, height in [(1440, 1100), (768, 1024), (390, 844)]:
        page.set_viewport_size({'width': width, 'height': height})
        response = page.goto(base + '/')
        assert response.status == 200
        assert page.locator('.stat > strong').all_text_contents() == ['10', '5', '5', '5', '10', '8,43/ 10']
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Dashboard excedeu a largura'
        page.screenshot(path=str(output / f'dashboard-{width}.png'), full_page=True)
        if width < 900:
            toggle = page.get_by_role('button', name='Abrir menu')
            toggle.click()
            assert page.locator('.menu-toggle').get_attribute('aria-expanded') == 'true'
            page.get_by_role('link', name='Alunos', exact=False).first.click()
        else:
            page.goto(base + '/alunos')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Listagem excedeu a largura'
        page.goto(base + '/alunos/cadastrar')
        assert page.locator('input[required]').count() == 4
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Formulário excedeu a largura'
        page.screenshot(path=str(output / f'formulario-{width}.png'), full_page=True)
        print(f'OK: dashboard, listagem e formulário em {width}px')
    page.goto(base + '/relatorios')
    page.locator('#report-select').select_option('notas')
    page.wait_for_url('**report=notas')
    assert page.locator('select[name=filter]').count() == 1
    # Executar o formulário real comprova a integração da tela com o backend.
    name = 'Navegador ' + str(time.time_ns())
    page.goto(base + '/alunos/cadastrar')
    page.get_by_label('Nome completo').fill(name)
    page.get_by_label('Data de nascimento').fill('2007-01-01')
    page.get_by_label('E-mail').fill(name.replace(' ', '') + '@example.com')
    page.get_by_label('Telefone com DDD').fill('(11) 99999-9999')
    page.get_by_role('button', name='Salvar aluno').click()
    page.wait_for_url('**/alunos')
    row = page.locator('tbody tr').filter(has_text=name)
    row.get_by_role('link', name='Editar').click()
    page.get_by_label('Nome completo').fill(name + ' atualizado')
    page.get_by_role('button', name='Salvar aluno').click()
    page.wait_for_url('**/alunos')
    page.locator('tbody tr').filter(has_text=name + ' atualizado').get_by_role('link', name='Excluir').click()
    page.get_by_role('checkbox').check()
    page.get_by_role('button', name='Confirmar exclusão').click()
    page.wait_for_url('**/alunos')
    assert page.locator('tbody tr').filter(has_text=name).count() == 0
    print('OK: cadastro, edição e exclusão pelo navegador')
    assert not errors, errors
    for path in ['.env', 'database.py', 'models.py', 'sql/seed.sql', 'templates/base.html', '.git/config', 'README.md']:
        assert page.request.get(base + '/' + path).status == 404, path
        print('OK: acesso bloqueado a ' + path)
    browser.close()
print('Navegação, dimensões, JavaScript e proteção de arquivos internos verificados.')
