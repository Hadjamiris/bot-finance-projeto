import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode # Importado para corrigir o negrito

# 🔒 COLOQUE SEU NOVO TOKEN AQUI (após dar /revoke no BotFather)
TOKEN = "8895963866:AAFQpSk7R-RE01BhYuQF9Dd91EzJn0MtJGw"

# Cria banco de dados
def criar_banco():
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            salario REAL DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            valor REAL,
            categoria TEXT,
            descricao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Oi! Sou seu bot de finanças 💰\n\n"
        "Comandos:\n"
        "/salario 2800 - define seu salário\n"
        "/gasto 45 mercado - registra gasto\n"
        "/relatorio - vê resumo do mês\n\n"
        "Ou só me manda: '50 gasolina' que eu já entendo"
    )

# Define salário
async def salario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(context.args[0])
        user_id = update.message.from_user.id

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO usuarios (user_id, salario) VALUES (?,?)", (user_id, valor))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"Salário de R${valor:.2f} registrado ✅")
    except:
        await update.message.reply_text("Use assim: /salario 2800")

# Registra gasto
async def registrar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        user_id = update.message.from_user.id

        # Se usou o comando /gasto 45 mercado
        if context.args:
            if len(context.args) < 2:
                raise ValueError("Faltou a categoria")
            valor = float(context.args[0])
            categoria = context.args[1].capitalize()
            descricao = ' '.join(context.args[1:])
        # Se mandou "45 mercado" direto (sem barra)
        else:
            partes = texto.split()
            if len(partes) < 2:
                raise ValueError("Faltou a categoria")
            valor = float(partes[0])
            categoria = partes[1].capitalize()
            descricao = ' '.join(partes[1:])

        # Categorização automática básica
        cat_map = {
            'mercado': 'Alimentação', 'ifood': 'Alimentação', 'lanche': 'Alimentação',
            'gasolina': 'Transporte', 'uber': 'Transporte', 'onibus': 'Transporte',
            'aluguel': 'Moradia', 'luz': 'Moradia', 'agua': 'Moradia',
            'racao': 'Pets', 'pet': 'Pets', 'veterinario': 'Pets'
        }
        categoria_final = cat_map.get(categoria.lower(), categoria)

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO gastos (user_id, valor, categoria, descricao) VALUES (?,?,?,?)",
                       (user_id, valor, categoria_final, descricao))
        conn.commit()

        # Soma da categoria
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE user_id =? AND categoria =?", (user_id, categoria_final))
        total_cat = cursor.fetchone()[0] or 0.0
        conn.close()

        await update.message.reply_text(
            f"R${valor:.2f} adicionado em *{categoria_final}* ✅\n"
            f"Total em {categoria_final} esse mês: R${total_cat:.2f}",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text("Formato incorreto. Use: '50 mercado' ou /gasto 50 mercado")

# Gera relatório
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    # Pega salário
    cursor.execute("SELECT salario FROM usuarios WHERE user_id =?", (user_id,))
    resultado = cursor.fetchone()
    salario = resultado[0] if resultado else 0

    # Soma gastos por categoria
    cursor.execute('''
        SELECT categoria, SUM(valor) as total
        FROM gastos
        WHERE user_id =?
        GROUP BY categoria
        ORDER BY total DESC
    ''', (user_id,))
    gastos = cursor.fetchall()
    conn.close()

    total_gasto = sum([g[1] for g in gastos])
    saldo = salario - total_gasto

    msg = f"📊 *Relatório do Mês*\n\n"
    msg += f"💰 *Salário:* R${salario:.2f}\n"
    msg += f"📉 *Total gasto:* R${total_gasto:.2f}\n"
    msg += f"⚖️ *Saldo restante:* R${saldo:.2f}\n\n"
    msg += "*Por categoria:*\n"

    for cat, valor in gastos:
        porc = (valor/salario*100) if salario > 0 else 0
        msg += f"• {cat}: R${valor:.2f} ({porc:.1f}%)\n"

    # Adicionado o parse_mode para os negritos e itálicos funcionarem
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# Inicia o bot
def main():
    criar_banco()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("salario", salario))
    app.add_handler(CommandHandler("gasto", registrar_gasto))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_gasto))

    print("Bot rodando... Pressione Ctrl+C para parar.")
    app.run_polling()

if __name__ == '__main__':
    main()