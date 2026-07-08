## Rule: Estética Dark Brutalist (Lookism Boss)

Sempre que for necessário criar ou modificar o design do portfólio deste workspace, o sistema deverá obedecer estritamente aos seguintes pilares:
1. **Fundo e Contraste Extremo:** O fundo deve ser SEMPRE Preto Puro (`#000000`). Nada de fundos claros ou clean. O texto é branco com efeitos de *Glow* radiante.
2. **Atmosfera Intimidadora:** Uso obrigatório da atmosfera "Shingen Yamazaki": Animações de cinzas caindo, bordas que somem na escuridão (*fade to black*) e interações sonoras (Web Audio API com drones graves).
3. **Tipografia e Tom de Voz:** Uso de *Bebas Neue* gigante e quebrada. O tom de voz das cópias (textos) em PT-BR deve ser agressivo, sombrio e imponente (ex: "INFRAESTRUTURA DAS SOMBRAS", "INVOCAR"). **Idioma 100% PT-BR Obrigatório**. Nenhuma palavra em inglês é permitida, mesmo para termos técnicos ou jargões da área de tecnologia (ex: "Data Warehouse" deve ser "Armazém de Dados", "Scraping" deve ser "Mineração de Dados", etc).
4. **Imagens Brutalistas:** Qualquer imagem real (dashboards, resultados) inserida no site não deve ter filtros de cor (grayscale). Elas devem entrar rasgando o layout, com suas cores reais chocando contra o fundo preto absoluto, como um flash de dados no meio da escuridão.

## Rule: Lenis Scroll Freeze Bug
Ao tentar sequestrar o mouse do usuário e rolar a página automaticamente usando `lenis.scrollTo()`, NUNCA utilize `lenis.stop()`. O `lenis.stop()` paralisa o motor inteiro, impossibilitando que scrolls programáticos concluam e disparando gatilhos infinitos travados. Para impedir que o usuário role a página durante uma animação, intercepte os eventos de 'wheel' e 'touchmove', ou use pointer-events.
