import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove broken CSS at lines 66-70 (orphan keyframes lines without selector)
broken_css = """        
            25% { filter: hue-rotate(90deg) contrast(2) invert(0.2); transform: translateX(-5px); }
            50% { filter: hue-rotate(-90deg) contrast(3); transform: translateX(5px); }
            75% { filter: hue-rotate(180deg) contrast(1); transform: translateY(-5px); }
            100% { filter: hue-rotate(0deg) contrast(1); transform: translateX(0); }
        }"""
html = html.replace(broken_css, '')

# 2. Remove broken cursor CSS block (lines 86-92)
broken_cursor_css = """        /* ─────────────────────────────────────────────
            pointer-events: none; z-index: 10000;
            transform: translate(-50%, -50%); will-change: transform;
            transition: opacity 0.2s, background 0.2s, box-shadow 0.2s;
            opacity: 0.5;
        }
        @media (pointer: coarse) { #cursor-glow, #cursor-dot { display: none; } }"""
html = html.replace(broken_cursor_css, '')

# 3. Add global-shatter CSS
shatter_css = """
        /* GLOBAL SHATTER CLICK EFFECT */
        .global-shatter {
            position: fixed; pointer-events: none; z-index: 9999;
            width: 60px; height: 60px; border: 2px solid var(--blood);
            border-radius: 50%; opacity: 0.8;
        }
"""
html = html.replace('    </style>', shatter_css + '    </style>', 1)

# 4. Fix btn-audio ID reference in JS (the button is btn-pulse which also handles pulse)
#    Add a dedicated mute button OR fix the reference
#    The pulse button is btn-pulse, we need a mute button separate - add it to nav
html = html.replace(
    '<button id="btn-pulse" class="btn-audio interact-snd">[ PULSAR SISTEMA ]</button>',
    '<button id="btn-audio" class="btn-audio interact-snd">[ ATIVAR AURA ]</button>\n            <button id="btn-pulse" class="btn-audio interact-snd">[ PULSAR SISTEMA ]</button>'
)

# 5. Wrap sections in tab-content divs
# First check if they are NOT already wrapped (look for tab-home div)
if 'id="tab-home"' not in html:
    # Wrap Hero + Stats in tab-home
    hero_start = '    <!-- HERO -->\n    <section class="sec-vh wrap">'
    hero_end_marker = '    <!-- CASES -->'
    
    idx_start = html.find(hero_start)
    idx_end = html.find(hero_end_marker)
    
    if idx_start != -1 and idx_end != -1:
        next_step_home = '''\n    <div class="next-step-wrap wrap" style="text-align: center; padding: 80px 0;">
        <button data-target="tab-engenharia" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase; font-family: var(--f-body); font-weight: 800;">[ AVANÇAR PARA PROJETOS -> ]</button>
    </div>\n'''
        hero_block = html[idx_start:idx_end]
        html = html[:idx_start] + '<div id="tab-home" class="tab-content tab-active">\n' + hero_block + next_step_home + '</div>\n\n    ' + html[idx_end:]

# Wrap Cases section in tab-engenharia
if 'id="tab-engenharia"' not in html:
    cases_start = '    <!-- CASES -->\n    <section id="work"'
    certs_start = '    <!-- CERTIFICADOS -->'
    
    idx_start = html.find(cases_start)
    idx_end = html.find(certs_start)
    
    if idx_start != -1 and idx_end != -1:
        next_step_proj = '''\n    <div class="next-step-wrap wrap" style="text-align: center; padding: 80px 0;">
        <button data-target="tab-qualificacao" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase; font-family: var(--f-body); font-weight: 800;">[ AVANÇAR PARA CERTIFICADOS -> ]</button>
    </div>\n'''
        cases_block = html[idx_start:idx_end]
        html = html[:idx_start] + '<div id="tab-engenharia" class="tab-content">\n' + cases_block + next_step_proj + '</div>\n\n    ' + html[idx_end:]

# Wrap Certs section in tab-qualificacao
if 'id="tab-qualificacao"' not in html:
    certs_start = '    <!-- CERTIFICADOS -->\n    <section id="certificados"'
    main_end = '\n</main>'
    
    idx_start = html.find(certs_start)
    idx_end = html.find(main_end)
    
    if idx_start != -1 and idx_end != -1:
        next_step_cert = '''\n    <div class="next-step-wrap wrap" style="text-align: center; padding: 80px 0;">
        <button data-target="tab-home" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase; font-family: var(--f-body); font-weight: 800;">[ RETORNAR AO INÍCIO ]</button>
    </div>\n'''
        certs_block = html[idx_start:idx_end]
        html = html[:idx_start] + '<div id="tab-qualificacao" class="tab-content">\n' + certs_block + next_step_cert + '</div>\n' + html[idx_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! All bugs fixed.")
