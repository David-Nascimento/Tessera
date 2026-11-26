"""Gera as capturas de tela usadas no README (docs/screenshots/).

Requisitos:
    pip install playwright
    playwright install chromium

Uso:
    python scripts/screenshots.py
"""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'docs')
OUT = os.path.join(SITE, 'screenshots')
PAGES = ['index', 'projetos', 'tarefas', 'cronograma', 'relatorios', 'equipe']

os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()

    def shoot(name, width, height, out, full=True, scale=1.5):
        ctx = browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=scale)
        page = ctx.new_page()
        page.goto(f'file://{SITE}/{name}.html')
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(300)
        if not full:
            page.evaluate("document.querySelector('main').scrollIntoView()")
        page.screenshot(path=os.path.join(OUT, f'{out}.png'), full_page=full)
        ctx.close()
        print('ok', out)

    for name in PAGES:
        shoot(name, 1440, 900, name)
    shoot('index', 390, 844, 'mobile', full=False, scale=2)
    browser.close()
