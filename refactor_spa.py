import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Navigation
old_nav = r'<nav class="nav-links">.*?</nav>'
new_nav = """<nav class="nav-links">
            <a href="#" data-target="tab-home" class="link-glow interact-snd tab-link active-tab">[ INÍCIO ]</a>
            <a href="#" data-target="tab-engenharia" class="link-glow interact-snd tab-link">[ PROJETOS ]</a>
            <a href="#" data-target="tab-qualificacao" class="link-glow interact-snd tab-link">[ CERTIFICADOS ]</a>
            <button id="btn-pulse" class="btn-audio interact-snd">[ PULSAR SISTEMA ]</button>
        </nav>"""
html = re.sub(old_nav, new_nav, html, flags=re.DOTALL)

# 2. Add Tab CSS
css_to_add = """
        /* SPA TABS */
        .tab-content { display: none; opacity: 0; pointer-events: none; transition: opacity 0.5s ease-in-out; }
        .tab-content.tab-active { display: block; opacity: 1; pointer-events: auto; animation: fadeUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }
        .active-tab { color: var(--text-bright); text-shadow: var(--glow); border-bottom: 1px solid var(--text-bright); }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
"""
html = html.replace('/* ─────────────────────────────────────────────', css_to_add + '\n        /* ─────────────────────────────────────────────', 1)

# Remove heavy-glitch
html = re.sub(r'body\.heavy-glitch \{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'@keyframes screen-tear \{.*?\}', '', html, flags=re.DOTALL)

# Remove pulse glitch animation reference
html = html.replace("document.body.classList.add('heavy-glitch');", "")
html = html.replace("document.body.classList.remove('heavy-glitch');", "")

# 3. Wrap Sections
html = html.replace('<section class="sec-vh" style="position:relative;">', '<div id="tab-home" class="tab-content tab-active">\n    <section class="sec-vh" style="position:relative;">')
html = html.replace('</section>\n\n    <!-- PROJECTS SECTION -->', '</section>\n    <div class="next-step-wrap wrap" style="text-align: center; padding-bottom: 100px;">\n        <button data-target="tab-engenharia" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase;">[ AVANÇAR PARA PROJETOS -> ]</button>\n    </div>\n</div>\n\n    <!-- PROJECTS SECTION -->')

html = html.replace('<!-- PROJECTS SECTION -->\n    <section id="cases"', '<div id="tab-engenharia" class="tab-content">\n    <!-- PROJECTS SECTION -->\n    <section id="cases"')
html = html.replace('</section>\n\n    <!-- CERTIFICAÇÕES SECTION -->', '</section>\n    <div class="next-step-wrap wrap" style="text-align: center; padding-bottom: 100px;">\n        <button data-target="tab-qualificacao" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase;">[ AVANÇAR PARA CERTIFICADOS -> ]</button>\n    </div>\n</div>\n\n    <!-- CERTIFICAÇÕES SECTION -->')

html = html.replace('<!-- CERTIFICAÇÕES SECTION -->\n    <section id="certificacoes"', '<div id="tab-qualificacao" class="tab-content">\n    <!-- CERTIFICAÇÕES SECTION -->\n    <section id="certificacoes"')
html = html.replace('</section>\n\n</main>', '</section>\n    <div class="next-step-wrap wrap" style="text-align: center; padding-bottom: 100px;">\n        <button data-target="tab-home" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase;">[ RETORNAR AO INÍCIO ]</button>\n    </div>\n</div>\n\n</main>')

# 4. JavaScript Logic
hijack_regex = r'// THE HIJACK SEQUENCE.*?overlay\.addEventListener\(\'click\', async \(\) => \{.*?\n    \}\);'
new_overlay = """// OVERLAY INIT E TABS LOGIC
    const overlay = document.getElementById('enter-overlay');
    overlay.querySelector('.system-warning').textContent = '[ INICIAR SESSÃO ]';
    
    overlay.addEventListener('click', () => {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.style.display = 'none', 1000);
        AudioEngine.init();
    });

    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            
            tabContents.forEach(content => content.classList.remove('tab-active'));
            document.querySelectorAll('.nav-links .tab-link').forEach(navLink => navLink.classList.remove('active-tab'));
            
            const targetTab = document.getElementById(targetId);
            if(targetTab) targetTab.classList.add('tab-active');
            
            const headerLink = document.querySelector(`.nav-links .tab-link[data-target="${targetId}"]`);
            if(headerLink) headerLink.classList.add('active-tab');

            // Reset Scroll
            window.scrollTo(0, 0);
            if(typeof lenis !== 'undefined') lenis.scrollTo(0, {immediate: true});

            // Audio Effect
            if(AudioEngine.playSound) AudioEngine.playSound(300, 'sine', 0.1);
        });
    });"""

html = re.sub(hijack_regex, new_overlay, html, flags=re.DOTALL)

html = re.sub(r'function preventScroll\(e\).*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'function strikeTarget\(selector\).*?// Failsafe.*?\}\);.*?\}', '', html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
