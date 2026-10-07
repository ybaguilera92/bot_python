# bot.py — Bot de Telegram con saludo y respuestas predefinidas (FAQ).
# Activo 24/7: polling de Telegram + servidor HTTP de keep-alive para
# que el plan gratuito de Render nunca duerma el servicio.
# Requiere: python-telegram-bot (ver requirements.txt)

import os
import re
import threading
import unicodedata
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN", "8939662066:AAFKyKmD7w_q252cPzsUOXelV4m7m9i3Nvg")
PORT = int(os.environ.get("PORT", 8080))  # Render asigna PORT solo

# ------------------------------------------------------------------
# 1) TUS PREGUNTAS Y RESPUESTAS: edita esta lista a tu gusto.
#    - "pregunta": lo que se muestra en el botón del menú.
#    - "claves": palabras (sin acentos) que activan la respuesta
#      cuando alguien escribe en el chat.
#    - "respuesta": el texto que envía el bot.
# ------------------------------------------------------------------
FAQ = [
    {
        "pregunta": "Hola, ¿quién eres?",
        "claves": ["hola", "buenas", "quien eres", "que eres", "presentate"],
        "respuesta": (
            "¡Hola! 👋 Soy un bot de demostración hecho en Python con la "
            "librería python-telegram-bot. Saludo a quien llega, respondo "
            "a preguntas frecuentes y no me apago nunca: estoy 24/7 en la nube."
        ),
    },
    {
        "pregunta": "¿Qué sabes hacer?",
        "claves": ["que sabes hacer", "que haces", "funciones", "comandos"],
        "respuesta": (
            "Por ahora sé cuatro cosas bien hechas: saludar a quien llega, "
            "responder a mi lista de preguntas frecuentes, reconocer palabras "
            "clave en lo que escribes y estar disponible a cualquier hora. "
            "Escribe /ayuda para ver la lista completa."
        ),
    },
    {
        "pregunta": "¿Cuál es tu horario?",
        "claves": ["horario", "horas", "abierto", "cuando estas activo", "siempre"],
        "respuesta": (
            "Estoy activo 24 horas, los 7 días de la semana. No tengo horario "
            "ni vacaciones: vivo en un servicio gratuito de la nube (Render) "
            "y un cron me hace ping cada poco tiempo para que no me duerma. 🌙"
        ),
    },
    {
        "pregunta": "¿Cómo funcionas por dentro?",
        "claves": ["como funcionas", "como estas hecho", "tecnologia", "python"],
        "respuesta": (
            "Estoy escrito en Python. Telegram me pasa tus mensajes y yo "
            "busco palabras clave en tu texto: si alguna coincide con mi "
            "lista, devuelvo la respuesta guardada. Sin inteligencia "
            "artificial: solo preguntas y respuestas que puedes editar en "
            "la lista FAQ de bot.py."
        ),
    },
    {
        "pregunta": "¿Cuánto cuestas?",
        "claves": ["cuanto cuestas", "precio", "pagar", "coste", "gratis"],
        "respuesta": (
            "Para ti, nada: hablar conmigo es gratis. Para mi creador, "
            "también: el plan gratuito de Render más un ping de cron-job.org "
            "me mantienen vivo sin gastar un céntimo. 💸"
        ),
    },
    {
        "pregunta": "¿Quién te creó?",
        "claves": ["quien te creo", "creador", "autor", "dueno"],
        "respuesta": (
            "Me construyó mi dueño siguiendo una guía de 9 pasos: lo creó "
            "con @BotFather, escribió mi código (bot.py), lo subió a GitHub "
            "y me desplegó gratis en Render. Si quieres un bot como yo, "
            "sigue los mismos pasos."
        ),
    },
]

FALLBACK = (
    "Esa no la tengo en mi lista 🤔 Toca un botón del menú o escribe /ayuda "
    "para ver todo lo que sé responder."
)


# ------------------------------------------------------------------
# 2) TECLADO DE BOTONES Y UTILIDADES
# ------------------------------------------------------------------
def teclado():
    filas = [
        [InlineKeyboardButton(item["pregunta"], callback_data=f"faq:{i}")]
        for i, item in enumerate(FAQ)
    ]
    return InlineKeyboardMarkup(filas)


def normaliza(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------------
# 3) COMANDOS
# ------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "por ahí"
    await update.message.reply_text(
        f"¡Hola, {nombre}! 👋 Soy tu asistente personal.\n\n"
        "Toca un botón para ver una respuesta o escríbeme tu pregunta "
        "con tus propias palabras: busco palabras clave en el texto.",
        reply_markup=teclado(),
    )


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lineas = ["Esto es lo que sé responder:", ""]
    for i, item in enumerate(FAQ, start=1):
        lineas.append(f"{i}. {item['pregunta']}")
    lineas += ["", "Puedes escribirme con tus palabras o usar /start para ver los botones."]
    await update.message.reply_text("\n".join(lineas), reply_markup=teclado())


# ------------------------------------------------------------------
# 4) RESPUESTAS
# ------------------------------------------------------------------
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    consulta = update.callback_query
    await consulta.answer()
    idx = int(consulta.data.split(":")[1])
    await consulta.message.reply_text(FAQ[idx]["respuesta"])


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = normaliza(update.message.text or "")
    for item in FAQ:
        for clave in item["claves"]:
            if re.search(r"\b" + re.escape(normaliza(clave)) + r"\b", texto):
                await update.message.reply_text(item["respuesta"])
                return
    await update.message.reply_text(FALLBACK)


# ------------------------------------------------------------------
# 5) SERVIDOR HTTP DE KEEP-ALIVE (responde a los pings del cron)
# ------------------------------------------------------------------
class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot activo")

    def log_message(self, *args):
        pass


# ------------------------------------------------------------------
# 6) ARRANQUE
# ------------------------------------------------------------------
def main():
    # Compatibilidad con Python 3.12+: crear el event loop explícitamente
    asyncio.set_event_loop(asyncio.new_event_loop())
    if not TOKEN:
        raise SystemExit(
            'Falta el token. Define la variable de entorno BOT_TOKEN antes '
            'de arrancar. Ejemplos:\n'
            '  Windows CMD:  set BOT_TOKEN=123456:ABC\n'
            '  PowerShell:   $env:BOT_TOKEN="123456:ABC"\n'
            '  Mac/Linux:    export BOT_TOKEN="123456:ABC"'
        )

    # Servidor HTTP en segundo plano: responde a los pings del cron.
    threading.Thread(
        target=lambda: HTTPServer(("0.0.0.0", PORT), Ping).serve_forever(),
        daemon=True,
    ).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    print("Bot arrancado y a la escucha. Pulsa Ctrl+C para detenerlo.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()