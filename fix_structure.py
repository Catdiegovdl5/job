with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the broken line created by the bad replacement
bad = '''            <section class="wrap sec-py">
            <div class="cases-grid"> onclick="window.open('https://github.com/Catdiegovdl5/scan','_blank')" style="cursor:pointer;">
                <div class="case-num">13</div>'''

good = '''            <section class="wrap sec-py">
            <div class="cases-grid">

            <div class="case-item fade-in interact-snd" id="case-13" onclick="window.open('https://github.com/Catdiegovdl5/scan','_blank')" style="cursor:pointer;">
                <div class="case-num">13</div>'''

html = html.replace(bad, good)

# Remove the extra </div> after case-12 that we accidentally added
bad2 = '''            </div>
            </div>
        </div>
    </section>

            <section class="wrap sec-py">'''
good2 = '''            </div>
        </div>
    </section>

            <section class="wrap sec-py">'''
html = html.replace(bad2, good2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML structure fixed!")
