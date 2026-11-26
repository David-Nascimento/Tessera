#!/usr/bin/env python3
"""Gera as páginas estáticas do Tessera em docs/.

Uso:
    python scripts/build.py                 # gera docs/*.html
    python scripts/build.py --canvas DIR    # também gera as telas no formato de canvas (.dc.html)

Todas as telas compartilham os mesmos tokens (cores, bordas, tipografia) e
componentes (sidebar, topbar, cartões, pills de status, barras hachuradas).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'docs')
CANVAS = sys.argv[sys.argv.index('--canvas') + 1] if '--canvas' in sys.argv else None

# ---------- tokens ----------
BG, SIDE, SURF, LINE, LINE2 = '#0E0F11', '#121316', '#17181B', '#24252A', '#222328'
TXT, MUT, MUT2 = '#ECECEE', '#8C8D96', '#A9AAB2'
BLUE, ORANGE, GREEN, GRAY = '#4C8DFF', '#FF8A3D', '#3DDC84', '#8C8D96'
ST = {
    'and': ('Em andamento', 'rgba(76,141,255,0.14)', '#8FB6FF', BLUE),
    'ris': ('Em risco', 'rgba(255,138,61,0.14)', '#FFAA70', ORANGE),
    'ok':  ('Concluído', 'rgba(61,220,132,0.14)', '#6FE6A4', GREEN),
    'todo': ('A fazer', 'rgba(140,141,150,0.16)', '#B9BAC1', GRAY),
}
CARD = f'border: 1px solid {LINE}; border-radius: 14px; background: {SURF}; padding: 20px'
H2 = 'margin: 0; font-size: 15px; font-weight: 600'
SUB = f'font-size: 12px; color: {MUT}'

def hatch(c, w=1.5, gap=5):
    return f'repeating-linear-gradient(135deg, {c} 0 {w}px, transparent {w}px {gap}px)'

def pill(k):
    t, bg, fg, _ = ST[k]
    return f'<span style="font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 999px; background: {bg}; color: {fg}; white-space: nowrap">{t}</span>'

def dot(c, s=6):
    return f'<span style="width: {s}px; height: {s}px; border-radius: 50%; background: {c}; flex: none"></span>'

def chip(t):
    return f'<span style="font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #2A2B31; color: {MUT2}">{t}</span>'

def bar(pct, c, h=4):
    return f'<div style="height: {h}px; border-radius: 4px; background: #24252B"><div style="width: {pct}%; height: 100%; border-radius: 4px; background: {c}"></div></div>'

def head2(title, sub=None, right=''):
    s = f'<span style="{SUB}">{sub}</span>' if sub else ''
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px">'
            f'<div style="display: flex; flex-direction: column; gap: 2px"><h2 style="{H2}">{title}</h2>{s}</div>{right}</div>')

def legend(items):
    out = ''
    for label, style in items:
        out += f'<span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; {style}"></span>{label}</span>'
    return f'<div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: {MUT2}">{out}</div>'

LEG_PLAN = f'border: 1px solid {BLUE}; box-sizing: border-box; background: {hatch(BLUE, 1.5, 4)}'
SOLID_GREEN = f'background: repeating-linear-gradient(135deg, {GREEN} 0 3px, #2DB86C 3px 5px)'

# ---------- data (ilustrativo) ----------
PROJECTS = [
    ('AI Network Guardian', 'and', 62, 'Monitoramento de rede com IA — fase 5 de 8', ['React', 'FastAPI', 'IA'], '15/12', 18, BLUE),
    ('QA AI Agent', 'ris', 41, 'Dashboard de pipelines de teste com agente de IA', ['Jenkins', 'Jira API'], '10/12', 12, ORANGE),
    ('k6-performance', 'and', 74, 'Testes de carga e stress com métricas no Grafana', ['k6', 'Grafana'], '05/12', 9, BLUE),
    ('Karate API Framework', 'ok', 100, 'Testes de API em estilo empresarial', ['Karate', 'Java'], '22/11', 31, GREEN),
    ('Portfólio de QA', 'and', 85, 'Site com todos os projetos de automação', ['GitHub Pages'], '30/11', 4, BLUE),
    ('monitor-internet', 'and', 55, 'Monitoramento de Wi-Fi e do PC', ['Docker', 'Prometheus', 'Grafana'], '12/12', 7, BLUE),
    ('Ruby E2E Framework', 'ok', 100, 'Automação E2E com Selenium + Cucumber + RSpec', ['Ruby', 'Selenium'], '19/11', 26, GREEN),
    ('Observability Stack', 'ris', 30, 'Jenkins, Docker e Grafana em Docker Compose', ['Jenkins', 'Docker'], '20/12', 11, ORANGE),
]

NAV = [('Main', 'Visão geral', 'index'), ('Projetos', 'Projetos', 'projetos'), ('Tarefas', 'Tarefas', 'tarefas'),
       ('Cronograma', 'Cronograma', 'cronograma'), ('Relatorios', 'Relatórios', 'relatorios'), ('Equipe', 'Equipe', 'equipe')]
ICONS = {
    'Main': '<rect x="3" y="3" width="7" height="9" rx="1"></rect><rect x="14" y="3" width="7" height="5" rx="1"></rect><rect x="14" y="12" width="7" height="9" rx="1"></rect><rect x="3" y="16" width="7" height="5" rx="1"></rect>',
    'Projetos': '<path d="M3 7h18M3 12h18M3 17h12"></path>',
    'Tarefas': '<path d="M9 11l3 3 8-8"></path><path d="M20 12v7a2 2 0 01-2 2H6a2 2 0 01-2-2V5a2 2 0 012-2h9"></path>',
    'Cronograma': '<rect x="3" y="4" width="18" height="17" rx="2"></rect><path d="M3 9h18M8 2v4M16 2v4"></path>',
    'Relatorios': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"></path>',
    'Equipe': '<circle cx="9" cy="8" r="3.5"></circle><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5M16 4.5a3.5 3.5 0 010 7M18 14.8c1.9.7 3.1 2.6 3.5 5.2"></path>',
}

def href(stem, mode):
    if mode == 'dc':
        return f'{stem}.dc.html'
    return dict((a, c) for a, _, c in NAV)[stem] + '.html'

def sidebar(active, mode):
    links = ''
    for stem, label, _ in NAV:
        on = stem == active
        st = (f'background: #1C1D22; color: {TXT}; border: 1px solid #2A2B31' if on else f'color: {MUT2}; border: 1px solid transparent')
        cur = ' aria-current="page"' if on else ''
        links += (f'<a href="{href(stem, mode)}"{cur} style="display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; {st}">'
                  f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{ICONS[stem]}</svg>{label}</a>')
    favs = ''
    for name, *_, c in PROJECTS[:3]:
        favs += f'<a href="{href("Projetos", mode)}" style="display: flex; align-items: center; gap: 10px; padding: 8px 10px; color: {MUT2}"><span style="width: 8px; height: 8px; border-radius: 2px; background: {c}"></span>{name}</a>'
    lab = f'font-size: 11px; font-weight: 600; color: {MUT}; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 10px 8px'
    return f'''<nav aria-label="Navegação principal" style="flex: 1 1 232px; max-width: 100%; box-sizing: border-box; padding: 24px 16px; border-right: 1px solid {LINE2}; display: flex; flex-direction: column; gap: 28px; background: {SIDE}">
<a href="{href('Main', mode)}" style="display: flex; align-items: center; gap: 10px; padding: 0 8px; color: {TXT}"><svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><rect x="1" y="1" width="11" height="11" rx="2" fill="{BLUE}"></rect><rect x="14" y="1" width="11" height="11" rx="2" fill="none" stroke="{TXT}" stroke-width="1.2"></rect><rect x="1" y="14" width="11" height="11" rx="2" fill="none" stroke="{TXT}" stroke-width="1.2"></rect><rect x="14" y="14" width="11" height="11" rx="2" fill="{ORANGE}"></rect></svg><span style="font-weight: 700; font-size: 17px; letter-spacing: -0.02em">Tessera</span></a>
<div style="display: flex; flex-direction: column; gap: 2px"><span style="{lab}">Espaço de trabalho</span>{links}</div>
<div style="display: flex; flex-direction: column; gap: 2px"><span style="{lab}">Favoritos</span>{favs}</div>
</nav>'''

def topbar(title, action='Novo projeto'):
    return f'''<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px">
<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; color: {MUT}">Espaço de trabalho / {title}</span><h1 style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.02em">{title}</h1></div>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px">
<label style="display: flex; align-items: center; gap: 8px; height: 40px; padding: 0 12px; border: 1px solid #26272D; border-radius: 9px; background: #16171A; color: {MUT}; min-width: 220px"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.5-3.5"></path></svg><span style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0)">Buscar</span><input type="search" placeholder="Buscar projetos, tarefas…" style="flex: 1; background: transparent; border: 0; outline: none; color: {TXT}; font: inherit; font-size: 13px"></label>
<button type="button" aria-label="Notificações" style="width: 44px; height: 40px; border: 1px solid #26272D; border-radius: 9px; background: #16171A; color: #C9CAD0; display: flex; align-items: center; justify-content: center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M6 8a6 6 0 1112 0c0 7 3 8 3 8H3s3-1 3-8M10 20a2 2 0 004 0"></path></svg></button>
<button type="button" style="height: 40px; padding: 0 16px; border: 0; border-radius: 9px; background: {TXT}; color: #111214; font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 6px"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M12 5v14M5 12h14"></path></svg>{action}</button>
</div></div>'''

def kpis(items):
    out = ''
    for label, value, foot, color in items:
        f = (f'<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: {color[1]}">{dot(color[0])}{foot}</span>'
             if color else f'<span style="{SUB}">{foot}</span>')
        out += (f'<div style="border: 1px solid {LINE}; border-radius: 14px; background: {SURF}; padding: 18px; display: flex; flex-direction: column; gap: 10px">'
                f'<span style="font-size: 12px; color: #9A9BA3">{label}</span><span style="font-size: 28px; font-weight: 600; letter-spacing: -0.03em">{value}</span>{f}</div>')
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px">{out}</div>'

CB, CO, CG = (BLUE, '#8FB6FF'), (ORANGE, '#FFAA70'), (GREEN, '#6FE6A4')

def vbars(groups, maxv, ticks, height=200):
    """groups: [(label, [(value, style)])]"""
    tk = ''.join(f'<span>{t}</span>' for t in ticks)
    cols = ''
    for label, vals in groups:
        bars = ''.join(f'<div style="width: 42%; max-width: 18px; height: {v / maxv * 100:.1f}%; border-radius: 4px 4px 0 0; box-sizing: border-box; {s}"></div>' for v, s in vals)
        cols += (f'<div style="flex: 1; height: 100%; display: flex; flex-direction: column; align-items: center; gap: 8px">'
                 f'<div style="flex: 1; width: 100%; display: flex; align-items: flex-end; justify-content: center; gap: 3px">{bars}</div>'
                 f'<span style="font-size: 11px; color: {MUT}; height: 14px">{label}</span></div>')
    step = (height - 22) / (len(ticks) - 1)
    return (f'<div style="display: flex; gap: 10px; height: {height}px">'
            f'<div style="display: flex; flex-direction: column; justify-content: space-between; font-size: 11px; color: {MUT}; padding-bottom: 22px; text-align: right; min-width: 22px">{tk}</div>'
            f'<div style="flex: 1; display: flex; align-items: flex-end; justify-content: space-between; gap: 8px; background: repeating-linear-gradient(to top, #202127 0 1px, transparent 1px {step:.1f}px)">{cols}</div></div>')

PLAN_STYLE = f'border: 1px solid {BLUE}; border-bottom: 0; background: {hatch(BLUE)}'

# ---------- páginas ----------
def page_main(mode):
    weeks = [(f'S{i+1}', [(p, PLAN_STYLE), (d, SOLID_GREEN)]) for i, (p, d) in enumerate(zip(
        [28, 32, 30, 36, 34, 38, 33, 36, 40, 35], [22, 27, 30, 29, 31, 35, 26, 34, 37, 30]))]
    proj = ''
    for name, st, pct, desc, tags, due, n, c in [PROJECTS[i] for i in (0, 1, 2, 3)]:
        meta = {'AI Network Guardian': 'Fase 5 de 8 · 18 tarefas abertas', 'QA AI Agent': 'MVP · integração Jira atrasada'}.get(name, f'{"Entregue" if st == "ok" else "Prazo"} {due} · {n} tarefas')
        proj += (f'<div style="border: 1px solid {LINE2}; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; gap: 10px">'
                 f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 8px"><span style="font-weight: 500">{name}</span>{pill(st)}</div>'
                 f'{bar(pct, ST[st][3])}<span style="{SUB}">{meta}</span></div>')
    rows = [('Dashboard de latência no Grafana', 'monitor-internet', '27/11', 'and'),
            ('Conectar API do Jira ao agente', 'QA AI Agent', '28/11', 'ris'),
            ('Cenário de stress com 500 VUs', 'k6-performance', '02/12', 'and'),
            ('Detecção de anomalias com IA', 'AI Network Guardian', '04/12', 'ris'),
            ('Card do Karate no portfólio', 'Portfólio de QA', '24/11', 'ok')]
    return f'''{topbar('Visão geral')}
<section aria-label="Perfil" style="border: 1px solid {LINE}; border-radius: 16px; overflow: hidden; background: {SURF}">
<div style="height: 112px; background: linear-gradient(110deg, #F7C9D9 0%, #E2D0F5 30%, #C7DCF8 62%, #CFF0DF 100%)"></div>
<div style="display: flex; flex-direction: column; gap: 12px; padding: 0 24px 20px">
<div style="width: 76px; height: 76px; margin-top: -38px; border-radius: 18px; background: #23242A; border: 3px solid {SURF}; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 26px">DN</div>
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px">
<div style="display: flex; flex-direction: column; gap: 4px"><span style="font-size: 18px; font-weight: 600; letter-spacing: -0.015em">David Nascimento</span><span style="font-size: 13px; color: #9A9BA3">QA Automation Engineer · Projetos pessoais</span></div>
<div style="display: flex; flex-wrap: wrap; gap: 8px"><span style="display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 10px; border-radius: 999px; border: 1px solid #2A2B31; font-size: 12px; color: #C9CAD0">{dot(GREEN)}Disponível</span>
<a href="{href('Equipe', mode)}" style="display: inline-flex; align-items: center; height: 36px; padding: 0 14px; border-radius: 8px; border: 1px solid #2A2B31; font-size: 13px; color: {TXT}">Ver equipe</a></div></div></div></section>
{kpis([('Projetos ativos', '6', 'Em andamento', CB), ('Tarefas em risco', '5', 'Atenção', CO), ('Entregues no mês', '14', 'Concluído', CG), ('Horas registradas', '126 h', 'Últimos 30 dias', None)])}
<div style="display: flex; flex-wrap: wrap; gap: 12px">
<section aria-label="Vazão da equipe" style="flex: 3 1 460px; min-width: 0; {CARD}; display: flex; flex-direction: column; gap: 18px">
{head2('Vazão da equipe', 'Tarefas por semana', legend([('Planejadas', LEG_PLAN), ('Concluídas', SOLID_GREEN)]))}
{vbars(weeks, 40, [40, 30, 20, 10, 0], 300)}
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding-top: 16px; border-top: 1px solid {LINE2}"><div style="display: flex; flex-direction: column; gap: 4px"><span style="{SUB}">Média planejada</span><span style="font-size: 18px; font-weight: 600">34,2 / semana</span></div><div style="display: flex; flex-direction: column; gap: 4px"><span style="{SUB}">Média concluída</span><span style="font-size: 18px; font-weight: 600">30,1 / semana</span></div><div style="display: flex; flex-direction: column; gap: 4px"><span style="{SUB}">Eficiência</span><span style="font-size: 18px; font-weight: 600; color: #6FE6A4">88%</span></div></div></section>
<section aria-label="Projetos" style="flex: 2 1 320px; min-width: 0; {CARD}; display: flex; flex-direction: column; gap: 14px">
{head2('Projetos', None, f'<a href="{href("Projetos", mode)}" style="font-size: 12px">Ver todos</a>')}
<div style="display: flex; flex-direction: column; gap: 8px">{proj}</div></section></div>
<section aria-label="Próximas tarefas" style="{CARD}; display: flex; flex-direction: column; gap: 12px">
{head2('Próximas tarefas', None, f'<a href="{href("Tarefas", mode)}" style="font-size: 12px">Abrir quadro</a>')}
{table(['Tarefa', 'Projeto', 'Responsável', 'Prazo', 'Status'], [[t, p, 'David', d, pill(s)] for t, p, d, s in rows])}</section>'''

def table(headers, rows):
    th = ''.join(f'<th style="font-weight: 600; padding: 8px 10px; border-bottom: 1px solid {LINE2}">{h}</th>' for h in headers)
    body = ''
    for i, r in enumerate(rows):
        b = f'; border-bottom: 1px solid #1F2025' if i < len(rows) - 1 else ''
        body += '<tr>' + ''.join(f'<td style="padding: 12px 10px{b}{"" if j == 0 else "; color: " + MUT2}">{c}</td>' for j, c in enumerate(r)) + '</tr>'
    return (f'<div style="overflow-x: auto"><table style="width: 100%; min-width: 620px; border-collapse: collapse; font-size: 13px">'
            f'<thead><tr style="text-align: left; color: {MUT}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em">{th}</tr></thead><tbody>{body}</tbody></table></div>')

def filters(items):
    out = ''
    for i, (label, n) in enumerate(items):
        on = i == 0
        st = f'background: {TXT}; color: #111214; border: 1px solid {TXT}' if on else f'background: transparent; color: {MUT2}; border: 1px solid #2A2B31'
        out += f'<button type="button" aria-pressed="{"true" if on else "false"}" style="height: 36px; padding: 0 14px; border-radius: 999px; font-size: 13px; font-weight: 500; {st}">{label} <span style="opacity: 0.6">{n}</span></button>'
    return f'<div role="group" aria-label="Filtrar" style="display: flex; flex-wrap: wrap; gap: 8px">{out}</div>'

def page_projetos(mode):
    cards = ''
    for name, st, pct, desc, tags, due, n, c in PROJECTS:
        cards += f'''<article style="{CARD}; display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px"><div style="display: flex; align-items: center; gap: 10px"><span style="width: 32px; height: 32px; border-radius: 8px; border: 1px solid {c}; background: {hatch(c, 1.5, 5)}; flex: none"></span><h2 style="{H2}">{name}</h2></div>{pill(st)}</div>
<p style="margin: 0; font-size: 13px; line-height: 1.5; color: {MUT2}">{desc}</p>
<div style="display: flex; flex-wrap: wrap; gap: 6px">{''.join(chip(t) for t in tags)}</div>
<div style="display: flex; flex-direction: column; gap: 8px"><div style="display: flex; justify-content: space-between; font-size: 12px; color: {MUT}"><span>Progresso</span><span style="color: {TXT}; font-weight: 500">{pct}%</span></div>{bar(pct, ST[st][3], 6)}</div>
<div style="display: flex; justify-content: space-between; font-size: 12px; color: {MUT}; padding-top: 12px; border-top: 1px solid {LINE2}"><span>{"Entregue" if st == "ok" else "Prazo"} {due}</span><span>{n} tarefas</span></div>
</article>'''
    return f'''{topbar('Projetos')}
{filters([('Todos', 8), ('Em andamento', 4), ('Em risco', 2), ('Concluídos', 2)])}
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px">{cards}</div>'''

TASKS = {
    'todo': [('Documentar endpoints no README', 'Karate API Framework', '29/11', 'Baixa'),
             ('Criar alertas no Alertmanager', 'monitor-internet', '06/12', 'Média'),
             ('Seção de contato no portfólio', 'Portfólio de QA', '30/11', 'Baixa')],
    'and': [('Dashboard de latência no Grafana', 'monitor-internet', '27/11', 'Alta'),
            ('Cenário de stress com 500 VUs', 'k6-performance', '02/12', 'Alta'),
            ('Tela de dispositivos conectados', 'AI Network Guardian', '03/12', 'Média'),
            ('Thresholds por endpoint', 'k6-performance', '04/12', 'Média')],
    'ris': [('Conectar API do Jira ao agente', 'QA AI Agent', '28/11', 'Alta'),
            ('Detecção de anomalias com IA', 'AI Network Guardian', '04/12', 'Alta'),
            ('Pipeline Jenkins com Docker-in-Docker', 'Observability Stack', '05/12', 'Média')],
    'ok':  [('Card do Karate no portfólio', 'Portfólio de QA', '24/11', 'Baixa'),
            ('Relatório Cucumber em HTML', 'Ruby E2E Framework', '19/11', 'Média'),
            ('Testes de contrato com schema', 'Karate API Framework', '21/11', 'Alta')],
}
PRIO = {'Alta': ORANGE, 'Média': BLUE, 'Baixa': GRAY}

def page_tarefas(mode):
    cols = ''
    for k, items in TASKS.items():
        t, _, fg, c = ST[k]
        cards = ''
        for title, proj, due, pr in items:
            cards += f'''<article style="border: 1px solid {LINE}; border-radius: 10px; background: #1B1C20; padding: 14px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 13px; font-weight: 500; line-height: 1.4">{title}</span>
<div style="display: flex; flex-wrap: wrap; gap: 6px">{chip(proj)}</div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: {MUT}"><span style="display: inline-flex; align-items: center; gap: 6px"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="4" width="18" height="17" rx="2"></rect><path d="M3 9h18"></path></svg>{due}</span><span style="display: inline-flex; align-items: center; gap: 6px">{dot(PRIO[pr])}{pr}</span></div>
</article>'''
        cols += f'''<section aria-label="{t}" style="flex: 1 1 240px; min-width: 0; border: 1px solid {LINE}; border-radius: 14px; background: {SURF}; padding: 14px; display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; align-items: center; justify-content: space-between; padding: 2px 4px 6px; border-bottom: 1px solid {LINE2}"><span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600">{dot(c, 8)}{t}</span><span style="font-size: 12px; color: {fg}">{len(items)}</span></div>
{cards}</section>'''
    return f'''{topbar('Tarefas', 'Nova tarefa')}
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px">{filters([('Quadro', ''), ('Lista', ''), ('Minhas tarefas', '')])}<span style="{SUB}">13 tarefas · 8 projetos</span></div>
<div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start">{cols}</div>'''

WEEKS = ['03/11', '10/11', '17/11', '24/11', '01/12', '08/12', '15/12', '22/12', '29/12', '05/01']
GANTT = [  # nome, início (semanas), duração, progresso%, status
    ('AI Network Guardian', 0.0, 6.4, 62, 'and'), ('QA AI Agent', 1.0, 5.0, 41, 'ris'),
    ('k6-performance', 2.0, 3.4, 74, 'and'), ('Karate API Framework', 0.0, 2.9, 100, 'ok'),
    ('Portfólio de QA', 2.6, 1.4, 85, 'and'), ('monitor-internet', 2.3, 3.9, 55, 'and'),
    ('Ruby E2E Framework', 0.0, 2.3, 100, 'ok'), ('Observability Stack', 3.0, 4.6, 30, 'ris'),
]

def page_cronograma(mode):
    N = len(WEEKS)
    hdr = ''.join(f'<span style="flex: 1; font-size: 11px; color: {MUT}; padding-left: 6px; border-left: 1px solid {LINE2}">{w}</span>' for w in WEEKS)
    grid = f'repeating-linear-gradient(to right, {LINE2} 0 1px, transparent 1px {100 / N:.4f}%)'
    today = (3 + 2 / 7) / N * 100
    rows = ''
    for name, s, d, p, st in GANTT:
        c = ST[st][3]
        rows += f'''<div style="display: flex; align-items: center; min-height: 52px; border-bottom: 1px solid #1F2025">
<div style="width: 200px; flex: none; display: flex; flex-direction: column; gap: 4px; padding-right: 12px"><span style="font-size: 13px; font-weight: 500">{name}</span><span style="font-size: 11px; color: {MUT}">{p}% · {ST[st][0]}</span></div>
<div style="flex: 1; position: relative; height: 52px; background: {grid}">
<div style="position: absolute; top: 14px; height: 24px; left: {s / N * 100:.2f}%; width: {d / N * 100:.2f}%; border: 1px solid {c}; border-radius: 6px; box-sizing: border-box; background: {hatch(c, 1.5, 6)}; overflow: hidden"><div style="width: {p}%; height: 100%; background: {c}; opacity: 0.85"></div></div>
</div></div>'''
    ms = [('01/12', 'Release v1 do k6-performance', 'and'), ('05/12', 'Integração Jira no QA AI Agent', 'ris'),
          ('15/12', 'Fase 6 do AI Network Guardian', 'and'), ('22/11', 'Karate API Framework publicado', 'ok')]
    msl = ''.join(f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #1F2025"><span style="width: 52px; font-size: 12px; color: {MUT}">{d}</span><span style="flex: 1; font-size: 13px">{t}</span>{pill(s)}</div>' for d, t, s in ms)
    return f'''{topbar('Cronograma', 'Novo marco')}
<section aria-label="Linha do tempo" style="{CARD}; display: flex; flex-direction: column; gap: 16px">
{head2('Linha do tempo', 'Novembro 2026 — Janeiro 2027', legend([('Planejado', f'border: 1px solid {BLUE}; box-sizing: border-box; background: {hatch(BLUE, 1.5, 4)}'), ('Concluído do período', f'background: {BLUE}')]))}
<div style="overflow-x: auto"><div style="min-width: 900px">
<div style="display: flex; padding-bottom: 8px; border-bottom: 1px solid {LINE2}"><span style="width: 200px; flex: none; font-size: 11px; color: {MUT}; text-transform: uppercase; letter-spacing: 0.06em">Projeto</span><div style="flex: 1; display: flex">{hdr}</div></div>
<div style="position: relative">{rows}<div style="position: absolute; top: 0; bottom: 0; left: calc(200px + (100% - 200px) * {today / 100:.4f}); width: 0; border-left: 1px dashed #ECECEE"><span style="position: absolute; top: -2px; left: 6px; font-size: 11px; font-weight: 600; background: {TXT}; color: #111214; padding: 1px 6px; border-radius: 4px; white-space: nowrap">Hoje</span></div></div>
</div></div></section>
<section aria-label="Próximos marcos" style="{CARD}; display: flex; flex-direction: column; gap: 6px">{head2('Marcos')}{msl}</section>'''

def page_relatorios(mode):
    months = [('Jun', 180, 12), ('Jul', 240, 18), ('Ago', 310, 15), ('Set', 290, 22), ('Out', 380, 14), ('Nov', 420, 9)]
    FAIL = f'border: 1px solid {ORANGE}; border-bottom: 0; background: {hatch(ORANGE)}'
    tests = vbars([(m, [(p, PLAN_STYLE), (f * 5, FAIL)]) for m, p, f in months], 500, [500, 375, 250, 125, 0], 220)
    hours = [('AI Network Guardian', 38, BLUE), ('QA AI Agent', 24, ORANGE), ('k6-performance', 21, BLUE), ('monitor-internet', 16, BLUE), ('Karate API Framework', 14, GREEN), ('Observability Stack', 13, ORANGE)]
    hb = ''.join(f'''<div style="display: flex; align-items: center; gap: 12px"><span style="width: 160px; flex: none; font-size: 13px; color: {MUT2}">{n}</span><div style="flex: 1; height: 18px"><div style="width: {h / 40 * 100:.0f}%; height: 100%; border: 1px solid {c}; border-radius: 4px; box-sizing: border-box; background: {hatch(c, 1.5, 5)}"></div></div><span style="width: 40px; text-align: right; font-size: 12px; font-weight: 500">{h} h</span></div>''' for n, h, c in hours)
    dist = [(4, BLUE, 'Em andamento'), (2, ORANGE, 'Em risco'), (2, GREEN, 'Concluído')]
    seg = ''.join(f'<div style="flex: {n}; background: {c}"></div>' for n, c, _ in dist)
    dl = ''.join(f'<div style="display: flex; align-items: center; justify-content: space-between; font-size: 13px; padding: 10px 0; border-bottom: 1px solid #1F2025"><span style="display: inline-flex; align-items: center; gap: 8px; color: {MUT2}">{dot(c, 8)}{t}</span><span style="font-weight: 500">{n} projetos · {n / 8 * 100:.0f}%</span></div>' for n, c, t in dist)
    return f'''{topbar('Relatórios', 'Exportar')}
{filters([('Últimos 6 meses', ''), ('Trimestre', ''), ('Ano', '')])}
{kpis([('Taxa de conclusão', '78%', 'Acima da meta', CG), ('Tempo médio de ciclo', '3,4 dias', 'Em linha', CB), ('Falhas em aberto', '9', 'Acompanhar', CO), ('Testes executados', '1.820', 'Últimos 6 meses', None)])}
<div style="display: flex; flex-wrap: wrap; gap: 12px">
<section aria-label="Testes por mês" style="flex: 3 1 460px; min-width: 0; {CARD}; display: flex; flex-direction: column; gap: 18px">
{head2('Execuções de teste', 'Por mês', legend([('Aprovados', LEG_PLAN), ('Falhas (×5)', f'border: 1px solid {ORANGE}; box-sizing: border-box; background: {hatch(ORANGE, 1.5, 4)}')]))}
{tests}</section>
<section aria-label="Status dos projetos" style="flex: 2 1 300px; min-width: 0; {CARD}; display: flex; flex-direction: column; gap: 16px">
{head2('Status dos projetos', '8 projetos')}
<div style="display: flex; gap: 3px; height: 14px; border-radius: 4px; overflow: hidden">{seg}</div>
<div>{dl}</div></section></div>
<section aria-label="Horas por projeto" style="{CARD}; display: flex; flex-direction: column; gap: 16px">
{head2('Horas por projeto', 'Últimos 30 dias · 126 h no total')}
<div style="display: flex; flex-direction: column; gap: 12px">{hb}</div></section>'''

MEMBERS = [
    ('DN', 'David Nascimento', 'QA Automation Engineer', 'Responsável', 'linear-gradient(135deg, #F7C9D9, #E2D0F5)', 8, 82, 'and', 'Disponível'),
    ('CL', 'Claude', 'Assistente de IA', 'Design e código', 'linear-gradient(135deg, #E2D0F5, #C7DCF8)', 5, 46, 'and', 'Ativo'),
    ('GC', 'Gemini CLI', 'Agente de testes', 'Geração de cenários', 'linear-gradient(135deg, #C7DCF8, #CFF0DF)', 3, 35, 'and', 'Ativo'),
    ('JK', 'Jenkins', 'CI/CD', 'Pipelines', 'linear-gradient(135deg, #FDE2C8, #F7C9D9)', 4, 68, 'ris', 'Fila cheia'),
    ('GF', 'Grafana', 'Observabilidade', 'Dashboards e alertas', 'linear-gradient(135deg, #CFF0DF, #FDE2C8)', 3, 28, 'ok', 'Estável'),
]

def page_equipe(mode):
    cards = ''
    for ini, name, role, desc, grad, nproj, load, st, stt in MEMBERS:
        _, bg, fg, c = ST[st]
        cards += f'''<article style="{CARD}; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; align-items: center; gap: 14px"><div style="width: 52px; height: 52px; border-radius: 14px; background: {grad}; color: #1A1B1F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px; flex: none">{ini}</div>
<div style="display: flex; flex-direction: column; gap: 3px; min-width: 0"><h2 style="{H2}">{name}</h2><span style="font-size: 12px; color: {MUT2}">{role} · {desc}</span></div></div>
<div style="display: flex; justify-content: space-between; align-items: center"><span style="font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 999px; background: {bg}; color: {fg}">{stt}</span><span style="{SUB}">{nproj} projetos</span></div>
<div style="display: flex; flex-direction: column; gap: 8px"><div style="display: flex; justify-content: space-between; font-size: 12px; color: {MUT}"><span>Carga de trabalho</span><span style="color: {TXT}; font-weight: 500">{load}%</span></div>
<div style="height: 10px; border-radius: 3px; border: 1px solid #2A2B31; overflow: hidden"><div style="width: {load}%; height: 100%; border-right: 1px solid {c}; box-sizing: border-box; background: {hatch(c, 1.5, 5)}"></div></div></div>
</article>'''
    acts = [('DN', 'David Nascimento', 'concluiu', 'Card do Karate no portfólio', '24/11'),
            ('JK', 'Jenkins', 'falhou no build de', 'Observability Stack', '25/11'),
            ('CL', 'Claude', 'criou o design de', 'Tessera', '26/11'),
            ('GC', 'Gemini CLI', 'gerou 12 cenários para', 'k6-performance', '26/11')]
    al = ''.join(f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #1F2025"><span style="width: 30px; height: 30px; border-radius: 8px; background: #23242A; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex: none">{i}</span><span style="flex: 1; font-size: 13px; color: {MUT2}"><span style="color: {TXT}; font-weight: 500">{n}</span> {v} <span style="color: {TXT}">{o}</span></span><span style="{SUB}">{d}</span></div>' for i, n, v, o, d in acts)
    return f'''{topbar('Equipe', 'Convidar')}
<span style="{SUB}">Pessoas e ferramentas que movem os projetos.</span>
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px">{cards}</div>
<section aria-label="Atividade recente" style="{CARD}; display: flex; flex-direction: column; gap: 6px">{head2('Atividade recente')}{al}</section>'''

PAGES = [  # stem, título, função, altura
    ('Main', 'Tessera — Visão geral', page_main, 1330),
    ('Projetos', 'Tessera — Projetos', page_projetos, 900),
    ('Tarefas', 'Tessera — Tarefas', page_tarefas, 900),
    ('Cronograma', 'Tessera — Cronograma', page_cronograma, 960),
    ('Relatorios', 'Tessera — Relatórios', page_relatorios, 930),
    ('Equipe', 'Tessera — Equipe', page_equipe, 900),
]

ROOT_STYLE = f'min-height: 100vh; background: {BG}; color: {TXT}; font-family: Inter, system-ui, sans-serif; font-size: 14px; letter-spacing: -0.005em; display: flex; flex-wrap: wrap'
MAIN_STYLE = 'flex: 999 1 560px; min-width: 0; box-sizing: border-box; padding: 24px 32px 40px; display: flex; flex-direction: column; gap: 20px; max-width: 1240px'
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
BASE_CSS = f'body{{margin:0;background:{BG};-webkit-font-smoothing:antialiased}}\na{{color:#9DBEFF;text-decoration:none}}a:hover{{color:#C6D8FF}}\nbutton{{font-family:inherit;cursor:pointer}}'

def body(stem, fn, mode):
    return f'<div style="{ROOT_STYLE}">\n{sidebar(stem, mode)}\n<main style="{MAIN_STYLE}">\n{fn(mode)}\n</main>\n</div>'

def write_dc(stem, title, fn, h):
    html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
{BASE_CSS}
</style>
</helmet>
{body(stem, fn, 'dc')}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''
    open(os.path.join(CANVAS, f'{stem}.dc.html'), 'w').write(html)

def write_site(stem, title, fn, slug):
    html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Tessera — painel de gerenciamento de projetos em modo escuro (portfólio visual).">
{FONTS}
<style>
{BASE_CSS}
</style>
</head>
<body>
{body(stem, fn, 'site')}
</body>
</html>
'''
    open(os.path.join(SITE, f'{slug}.html'), 'w').write(html)

if __name__ == '__main__':
    os.makedirs(SITE, exist_ok=True)
    slugs = dict((a, c) for a, _, c in NAV)
    for stem, title, fn, h in PAGES:
        write_site(stem, title, fn, slugs[stem])
        if CANVAS:
            os.makedirs(CANVAS, exist_ok=True)
            write_dc(stem, title, fn, h)
    if not CANVAS:
        print('ok'); sys.exit(0)
    # canvas.json: 3 por linha
    boards, order, y, rowmax = {}, [], 0, 0
    for i, (stem, title, fn, h) in enumerate(PAGES):
        col = i % 3
        if col == 0 and i:
            y += rowmax + 120; rowmax = 0
        boards[f'{stem}.dc.html'] = {'x': col * 1520, 'y': y, 'w': 1440, 'h': h, 'expand': 'fill', 'is_interactive': True, 'title': title.replace('Tessera — ', '')}
        order.append(f'{stem}.dc.html'); rowmax = max(rowmax, h)
    cp = os.path.join(CANVAS, 'canvas.json')
    cj = json.load(open(cp)) if os.path.exists(cp) else {'v': 3, 'title': 'Tessera', 'pages': [], 'notes': {}, 'designSystems': []}
    cj['boards'], cj['order'] = boards, order
    cj['launch'] = {'view': 'canvas'}
    json.dump(cj, open(os.path.join(CANVAS, 'canvas.json'), 'w'), ensure_ascii=False)
    print('ok')
