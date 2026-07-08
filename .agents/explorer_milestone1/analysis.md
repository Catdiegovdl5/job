# Project Analysis - Portfolio Revamp

## 1. Project Structure Analysis

The project located at `C:\Users\99196\teamwork_projects\resume_e_portfolio_update\job` is a **static multi-page website** built using vanilla technologies (HTML5, CSS3, JavaScript) and styled with Tailwind CSS loaded via CDN.

### Key Directories and Files:
*   `index.html` (155,414 bytes) — Main home landing page.
*   `portfolio.html` (128,412 bytes) — Case studies/detailed portfolio page.
*   `google_apps_script.gs` (8,293 bytes) — Google Apps Script backend file containing webhook logic to save submissions to Google Sheets and notify via Telegram.
*   `assets/` — Stores images and dashboards (e.g. `assets/img/bofu.png`, `assets/img/tofu.png`). No compiled bundler files (Webpack, Vite, etc.) are present.
*   `certificados/` — Folder containing certification credentials/images.
*   `IMAGENS/` — Additional media resources.

### Build and Frontend Stack:
*   **CSS / Styling**: Tailwind CSS via CDN (`https://cdn.tailwindcss.com`) and custom style tags.
*   **Scroll Animations**: AOS (Animate On Scroll) library via CDN (`https://unpkg.com/aos@2.3.1/dist/aos.js`).
*   **3D Hover Cards**: Vanilla Tilt library via CDN (`https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.0/vanilla-tilt.min.js`).
*   **Vanilla JS Scripting**: Embedded `<script>` tags at the bottom of pages containing modular interactive logic (e.g. ROAS calculator, language toggles, tab-switchers, and modal qualifies).

---

## 2. Telegram Message Integration Analysis

There are three files containing Telegram notifications and integration logic:

### File 1: `google_apps_script.gs`
This is a Google Apps Script file designed to run on the Google Sheets App Suite server. It acts as the backend webhook target to store leads and dispatch notifications without exposing bot credentials client-side.

*   **Line 24-25**: Configuration variables where credentials are set:
    ```javascript
    const TELEGRAM_BOT_TOKEN = '7724330024:AAFtoSLgXVDlvNmeyPCVMnkWIqbk4wvLSVg'; // @mira262005_bot
    const TELEGRAM_CHAT_ID   = '1501131002';      // Seu chat_id já configurado
    ```
*   **Line 149-210**: Function `sendTelegramNotification(payload)` executing a `UrlFetchApp.fetch` POST call to the Telegram API:
    ```javascript
    function sendTelegramNotification(payload) {
      if (!TELEGRAM_BOT_TOKEN || TELEGRAM_BOT_TOKEN === 'SEU_TOKEN_AQUI') {
        console.warn('Token do Telegram não configurado. Configure TELEGRAM_BOT_TOKEN.');
        return;
      }
      // ... payload extraction ...
      const mensagem = `${iconeStatus} *${tituloStatus}*\n\n` +
        // ... markdown formatting ...
      const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
      const options = {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: mensagem,
          parse_mode: 'Markdown'
        }),
        muteHttpExceptions: true
      };
      try {
        const response = UrlFetchApp.fetch(url, options);
        // ... logging response ...
      } catch (err) {
        console.error('Erro ao enviar para Telegram:', err.toString());
      }
    }
    ```

### File 2: `index.html`
Contains fallback Telegram webhook and direct client-side integration logic.
*   **Line 1578-1584**: Client-side config object with an active (exposed) fallback Bot Token:
    ```javascript
    const CONFIG = {
        webhookUrl: '',
        
        // Fallback direto (apenas para testes locais — não expor em produção!)
        telegramBotToken: '7724330024:AAFtoSLgXVDlvNmeyPCVMnkWIqbk4wvLSVg', 
        telegramChatId: '1501131002'
    };
    ```
*   **Line 1600-1623**: Triggering a direct fetch to the Telegram sendMessage endpoint if no Webhook URL is supplied:
    ```javascript
    } else if (CONFIG.telegramBotToken) {
        const telegramMessage = `⚡ [TELEMETRIA DE FUNIL] ⚡\n` +
            `STATUS: ${statusTelemetria}\n\n` +
            `👤 Nome: ${name}\n` +
            `📧 Email: ${email}\n` +
            `🌐 URL: ${website}\n` +
            `📱 Zap: ${whatsapp}\n\n` +
            `📊 Faturamento: ${faturamento}\n` +
            `📈 Ads Spend: ${investimento}\n` +
            `🛠️ Gargalo: ${gargalo}`;

        // Disparo direto em background para o Telegram (Exposto - Apenas para testes!)
        fetch(`https://api.telegram.org/bot${CONFIG.telegramBotToken}/sendMessage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: CONFIG.telegramChatId,
                text: telegramMessage
            })
        }).catch(err => {
            console.warn('Erro ao enviar dados para o Telegram:', err);
        });
    }
    ```

### File 3: `portfolio.html`
Contains identical configuration fallback and direct client-side API trigger logic.
*   **Line 1294-1300**: Config object (token is empty here, but Chat ID is exposed):
    ```javascript
    const CONFIG = {
        webhookUrl: '', // Insira a URL do seu Google Apps Script aqui para ficar 100% seguro!
        
        // Mantenha os campos abaixo vazios no código público. Use apenas localmente se necessário.
        telegramBotToken: '', 
        telegramChatId: '1501131002'
    };
    ```
*   **Line 1316-1340**: Client-side fetch fallback call:
    ```javascript
    } else if (CONFIG.telegramBotToken) {
        const telegramMessage = `⚡ [TELEMETRIA DE FUNIL] ⚡\n` +
            `STATUS: ${statusTelemetria}\n\n` +
            `👤 Nome: ${name}\n` +
            `📧 Email: ${email}\n` +
            `🌐 URL: ${website}\n` +
            `📱 Zap: ${whatsapp}\n\n` +
            `📊 Faturamento: ${faturamento}\n` +
            `📈 Ads Spend: ${investimento}\n` +
            `🛠️ Gargalo: ${gargalo}`;

        // Disparo direto em background para o Telegram (Exposto - Apenas para testes!)
        fetch(`https://api.telegram.org/bot${CONFIG.telegramBotToken}/sendMessage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: CONFIG.telegramChatId,
                text: telegramMessage
            })
        }).catch(err => {
            console.warn('Erro ao enviar dados para o Telegram:', err);
        });
    }
    ```

---

## 3. Dark Mode Cyber/Tech Aesthetic Research

To transition the portfolio into a premium "Dark Mode Cyber/Tech" aesthetic using the requested libraries, the following libraries, CDNs, and integration specifications are recommended.

### A. GSAP (GreenSock Animation Platform)
GSAP handles layout transitions, page intro sequences, 3D interactive animations, and scroll-bound events.

*   **CDNs (latest stable 3.12.5)**:
    *   GSAP Core: `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`
    *   ScrollTrigger Plugin: `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js`
    *   TextPlugin (useful for typing or hacking scrambles): `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/TextPlugin.min.js`
*   **Example Integration**:
    ```javascript
    // Register plugins
    gsap.registerPlugin(ScrollTrigger, TextPlugin);

    // Dynamic neon lines drawing on scroll
    gsap.from(".cyber-grid-line", {
        scrollTrigger: {
            trigger: ".hero-section",
            start: "top top",
            end: "bottom top",
            scrub: true
        },
        scaleX: 0,
        transformOrigin: "left center",
        ease: "none"
    });
    ```

### B. Lenis Smooth Scrolling
Lenis provides smooth inertia trackpad/mousewheel scrolling, crucial for premium, fluid visual presentations when paired with GSAP ScrollTrigger.

*   **CDNs**:
    *   Lenis Core JS: `https://unpkg.com/lenis@1.1.13/dist/lenis.min.js`
    *   Lenis CSS: Inlined custom CSS structure to avoid external stylesheet latency:
        ```css
        html.lenis, html.lenis body {
          height: auto;
        }
        .lenis-smooth {
          scroll-behavior: auto !important;
        }
        .lenis-smooth [data-lenis-prevent] {
          overscroll-behavior: contain;
        }
        .lenis-stopped {
          overflow: hidden;
        }
        .lenis-scrolling iframe {
          pointer-events: none;
        }
        ```
*   **Example Initialization**:
    ```javascript
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        smoothWheel: true,
        smoothTouch: false
    });

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Sync with GSAP ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
    });
    gsap.ticker.lagSmoothing(0);
    ```

### C. Type (Typed.js)
For typing/terminal command lines and matrix cyber aesthetics.
*   **CDNs**:
    *   Typed.js Core: `https://unpkg.com/typed.js@2.1.0/dist/typed.umd.js`
*   **Example Initialization**:
    ```javascript
    new Typed('.scramble-target', {
        strings: ['GROWTH ENGINEER', 'PERFORMANCE ARCHITECT', 'DATA ENGINEER'],
        typeSpeed: 60,
        backSpeed: 30,
        backDelay: 2000,
        loop: true,
        cursorChar: '_'
    });
    ```

### D. Inspira UI Style Elements (Replicated in Vanilla JS/CSS)
Since Inspira UI is a React/Vue Tailwind component library, we can easily rebuild its premium visuals using vanilla JS + Tailwind classes:

1.  **Spotlight Card (Following mouse cursor)**:
    *   *HTML/CSS Structure*:
        ```html
        <div class="relative overflow-hidden rounded-xl border border-white/5 bg-[#0A0A0C] p-8 group spotlight-card">
            <!-- Glow background overlay -->
            <div class="pointer-events-none absolute -inset-px opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" 
                 style="background: radial-gradient(400px circle at var(--x) var(--y), rgba(16, 185, 129, 0.15), transparent 80%);"></div>
            <!-- Card Content -->
            <div class="relative z-10">...</div>
        </div>
        ```
    *   *JS Logic*:
        ```javascript
        document.querySelectorAll('.spotlight-card').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--x', `${x}px`);
                card.style.setProperty('--y', `${y}px`);
            });
        });
        ```

2.  **Cyber Grid / Cyberpunk Neon Accent lines**:
    *   *CSS*:
        ```css
        .cyber-grid {
            background-size: 40px 40px;
            background-image: 
                linear-gradient(to right, rgba(16, 185, 129, 0.04) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(16, 185, 129, 0.04) 1px, transparent 1px);
        }
        ```

3.  **Glassmorphism (Vercel-style blur panels)**:
    *   *Tailwind classes*:
        ```html
        <div class="backdrop-blur-xl bg-black/60 border border-white/10 shadow-[0_10px_50px_rgba(0,0,0,0.8)]"></div>
        ```
