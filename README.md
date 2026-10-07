# Bot de Telegram 24/7 — respuestas predefinidas
Bot en Python que saluda a quien llega, responde preguntas frecuentes conbotones y con palabras clave, y queda desplegado gratis las 24 horas.

# Archivos
- bot.py -> el bot completo (saludo, FAQ, keep-alive)
- requirements.txt -> dependencias (python-telegram-bot)
- checklist.txt -> checklist de despliegue
- guia.html -> genera el PDF con la guía de 9 pasos
# Arranque en local
1. Instala Python 3.11 o superior desde python.org.
2. Crea y activa el entorno virtual:python -m venv .venvWindows: .venv\Scripts\activateMac/Linux: source .venv/bin/activate
3. Instala las dependencias:pip install -r requirements.txt
4. Define el token de BotFather como variable de entorno:Windows CMD: set BOT_TOKEN=tu_tokenPowerShell: $env:BOT_TOKEN="tu_token"Mac/Linux: export BOT_TOKEN="tu_token"
5. Arranca el bot:python bot.py
# Despliegue gratis (Render + cron-job.org)
1. Sube bot.py y requirements.txt a un repositorio de GitHub.
2. En render.com: "New +", elige "Web Service" y conecta el repositorio.
3. Runtime: Python | Build: pip install -r requirements.txtStart: python bot.py | Instancia: Free
4. En "Environment", crea la variable BOT_TOKEN con tu token.
5. En cron-job.org, programa un GET cada 10 minutos a la URL de Renderpara que el servicio no se duerma.
6. Personaliza las preguntas editando la lista FAQ de bot.py y haz commit:Render redespliega solo.