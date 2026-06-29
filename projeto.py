import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode




# Cria o banco de dados e as tabelas
def criar_banco():
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    # Tabela para guardar salário do usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            salario REAL DEFAULT 0
        )
    ''')

    # Tabela para guardar os gastos
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

    # Tabela para guardar limite de cada categoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS limites (
            user_id INTEGER,
            categoria TEXT,
            limite REAL,
            PRIMARY KEY (user_id, categoria)
        )
    ''')

    conn.commit()
    conn.close()


# Mensagem inicial do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Oi! Sou seu bot de finanças 💰\n\n"
        "Comandos:\n"
        "/salario 2800\n"
        "/limite Alimentação 500\n"
        "/desativarlimite Alimentação\n"
        "/ativarlimite Alimentação 500\n"
        "/gasto 50 mercado\n"
        "/relatorio\n"
        "/listar\n"
        "/apagar 3\n\n"
        "/relatorioperiodo mensal\n"
        "Ou mande só: 50 gasolina"
    )


# Desativa o limite de uma categoria
async def desativar_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega a categoria digitada pelo usuário
        categoria = context.args[0].capitalize()

        # Pega o ID do usuário do Telegram
        user_id = update.message.from_user.id

        # Conecta ao banco de dados
        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Apaga o limite da categoria escolhida
        cursor.execute(
            "DELETE FROM limites WHERE user_id = ? AND categoria = ?",
            (user_id, categoria)
        )

        # Salva a alteração
        conn.commit()

        # Fecha a conexão
        conn.close()

        # Responde ao usuário
        await update.message.reply_text(
            f"✅ Limite da categoria {categoria} foi desativado."
        )

    except:
        # Mensagem caso o usuário digite o comando errado
        await update.message.reply_text(
            "Use assim: /desativarlimite Alimentação"
        )

# Ativa novamente o limite de uma categoria
async def ativar_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega a categoria digitada pelo usuário
        categoria = context.args[0].capitalize()

        # Pega o valor do limite digitado pelo usuário
        limite = float(context.args[1])

        # Pega o ID do usuário do Telegram
        user_id = update.message.from_user.id

        # Conecta ao banco de dados
        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Cria ou atualiza o limite da categoria
        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, categoria, limite)
        )

        # Salva as alterações
        conn.commit()

        # Fecha a conexão
        conn.close()

        # Mensagem de sucesso
        await update.message.reply_text(
            f"✅ Limite da categoria {categoria} foi ativado com R${limite:.2f}."
        )

    except:
        # Mensagem caso o usuário digite errado
        await update.message.reply_text(
            "Use assim: /ativarlimite Alimentação 500"
        )

# Salva o salário do usuário e cria limites automáticos
async def salario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega o salário digitado pelo usuário
        valor = float(context.args[0])

        # Pega o ID do usuário
        user_id = update.message.from_user.id

        # Calcula os limites com base no salário
        limite_alimentacao = valor * 0.30
        limite_transporte = valor * 0.15
        limite_moradia = valor * 0.25
        limite_saude = valor * 0.10
        limite_lazer = valor * 0.10
        limite_compras = valor * 0.10

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Salva o salário
        cursor.execute(
            "INSERT OR REPLACE INTO usuarios (user_id, salario) VALUES (?, ?)",
            (user_id, valor)
        )

        # Salva os limites automáticos
        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Alimentação", limite_alimentacao)
        )

        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Transporte", limite_transporte)
        )

        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Moradia", limite_moradia)
        )

        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Saúde", limite_saude)
        )

        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Lazer", limite_lazer)
        )

        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, "Compras", limite_compras)
        )

        conn.commit()
        conn.close()

        await update.message.reply_text(
            f"Salário de R${valor:.2f} registrado ✅\n\n"
            f"Limites automáticos criados:\n"
            f"🍔 Alimentação: R${limite_alimentacao:.2f}\n"
            f"🚗 Transporte: R${limite_transporte:.2f}\n"
            f"🏠 Moradia: R${limite_moradia:.2f}\n"
            f"💊 Saúde: R${limite_saude:.2f}\n"
            f"🎉 Lazer: R${limite_lazer:.2f}\n"
            f"🛍️ Compras: R${limite_compras:.2f}"
        )

    except:
        await update.message.reply_text("Use assim: /salario 2800")


# Define limite para uma categoria
async def definir_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega a categoria digitada
        categoria = context.args[0].capitalize()

        # Pega o valor do limite
        limite = float(context.args[1])

        # Pega o ID do usuário
        user_id = update.message.from_user.id

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Salva ou atualiza o limite da categoria
        cursor.execute(
            "INSERT OR REPLACE INTO limites (user_id, categoria, limite) VALUES (?, ?, ?)",
            (user_id, categoria, limite)
        )

        conn.commit()
        conn.close()

        await update.message.reply_text(
            f"Limite de R${limite:.2f} definido para {categoria} ✅"
        )

    except:
        await update.message.reply_text("Use assim: /limite Alimentação 1500")


# Registra um gasto
async def registrar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        user_id = update.message.from_user.id

        # Caso use: /gasto 45 mercado
        if context.args:
            valor = float(context.args[0])
            categoria = context.args[1].lower()
            descricao = ' '.join(context.args[1:])

        # Caso use: 45 mercado
        else:
            partes = texto.split()
            valor = float(partes[0])
            categoria = partes[1].lower()
            descricao = ' '.join(partes[1:])

        # Mapa de palavras para categorias
        cat_map = {
            'mercado': 'Alimentação',
            'ifood': 'Alimentação',
            'lanche': 'Alimentação',
            'restaurante': 'Alimentação',
            'padaria': 'Alimentação',
            'pizza': 'Alimentação',

            'gasolina': 'Transporte',
            'uber': 'Transporte',
            'onibus': 'Transporte',
            'ônibus': 'Transporte',
            'estacionamento': 'Transporte',

            'aluguel': 'Moradia',
            'luz': 'Moradia',
            'agua': 'Moradia',
            'água': 'Moradia',
            'internet': 'Moradia',

            'remedio': 'Saúde',
            'remédio': 'Saúde',
            'consulta': 'Saúde',
            'farmacia': 'Saúde',
            'farmácia': 'Saúde',

            'cinema': 'Lazer',
            'show': 'Lazer',
            'festa': 'Lazer',
            'viagem': 'Lazer',

            'roupa': 'Compras',
            'sapato': 'Compras',
            'maquiagem': 'Compras',
            'presente': 'Compras',

            'faculdade': 'Educação',
            'curso': 'Educação',
            'livro': 'Educação',

            'racao': 'Pets',
            'ração': 'Pets',
            'pet': 'Pets',
            'veterinario': 'Pets',
        }

        # Pega a categoria automática
        categoria_final = cat_map.get(categoria, categoria.capitalize())

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Salva o gasto no banco
        cursor.execute(
            "INSERT INTO gastos (user_id, valor, categoria, descricao) VALUES (?, ?, ?, ?)",
            (user_id, valor, categoria_final, descricao)
        )

        conn.commit()

        # Soma quanto já foi gasto nessa categoria
        cursor.execute(
            "SELECT SUM(valor) FROM gastos WHERE user_id = ? AND categoria = ?",
            (user_id, categoria_final)
        )

        total_categoria = cursor.fetchone()[0] or 0.0

        # Busca o limite dessa categoria
        cursor.execute(
            "SELECT limite FROM limites WHERE user_id = ? AND categoria = ?",
            (user_id, categoria_final)
        )

        resultado_limite = cursor.fetchone()

        conn.close()

        # Mensagem normal
        mensagem = (
            f"R${valor:.2f} adicionado em *{categoria_final}* ✅\n"
            f"Total em {categoria_final}: R${total_categoria:.2f}"
        )

        # Se tiver limite, verifica se passou
        if resultado_limite:
            limite = resultado_limite[0]

            if total_categoria > limite:
                mensagem += (
                    f"\n\n⚠️ Você passou do limite de *{categoria_final}*!\n"
                    f"Limite: R${limite:.2f}\n"
                    f"Gasto atual: R${total_categoria:.2f}"
                )

        await update.message.reply_text(
            mensagem,
            parse_mode=ParseMode.MARKDOWN
        )

    except:
        await update.message.reply_text("Use assim: 50 mercado ou /gasto 50 mercado")


# Mostra o relatório geral
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    # Busca salário
    cursor.execute(
        "SELECT salario FROM usuarios WHERE user_id = ?",
        (user_id,)
    )

    resultado = cursor.fetchone()
    salario = resultado[0] if resultado else 0

    # Busca gastos por categoria
    cursor.execute('''
        SELECT categoria, SUM(valor)
        FROM gastos
        WHERE user_id = ?
        GROUP BY categoria
        ORDER BY SUM(valor) DESC
    ''', (user_id,))

    gastos = cursor.fetchall()
    conn.close()

    # Soma todos os gastos
    total_gasto = sum([g[1] for g in gastos])

    # Calcula o saldo restante
    saldo = salario - total_gasto

    msg = "📊 *Relatório*\n\n"
    msg += f"💰 Salário: R${salario:.2f}\n"
    msg += f"📉 Total gasto: R${total_gasto:.2f}\n"
    msg += f"⚖️ Saldo restante: R${saldo:.2f}\n\n"
    msg += "*Por categoria:*\n"

    # Mostra cada categoria com seu total
    for categoria, valor in gastos:
        msg += f"• {categoria}: R${valor:.2f}\n"

    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.MARKDOWN
    )


# Lista os gastos cadastrados
async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    # Busca todos os gastos do usuário
    cursor.execute(
        "SELECT id, categoria, valor, descricao FROM gastos WHERE user_id = ?",
        (user_id,)
    )

    gastos = cursor.fetchall()
    conn.close()

    # Se não tiver gasto cadastrado
    if len(gastos) == 0:
        await update.message.reply_text("Nenhum gasto cadastrado.")
        return

    texto = "📋 *Seus gastos:*\n\n"

    # Monta a lista de gastos com ID
    for id_gasto, categoria, valor, descricao in gastos:
        texto += f"ID {id_gasto} - {categoria} - R${valor:.2f} - {descricao}\n"

    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)


# Apaga um gasto pelo ID
async def apagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega o ID do usuário
        user_id = update.message.from_user.id

        # Pega o ID do gasto que o usuário quer apagar
        id_gasto = int(context.args[0])

        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Apaga o gasto somente se ele for daquele usuário
        cursor.execute(
            "DELETE FROM gastos WHERE id = ? AND user_id = ?",
            (id_gasto, user_id)
        )

        conn.commit()
        conn.close()

        await update.message.reply_text(f"Gasto ID {id_gasto} apagado ✅")

    except:
        await update.message.reply_text("Use assim: /apagar 3")

# Gera relatório por período: mensal, trimestral, semestral ou anual
async def relatorio_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pega o tipo de período digitado pelo usuário
        periodo = context.args[0].lower()

        # Pega o ID do usuário
        user_id = update.message.from_user.id

        # Conecta ao banco
        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()

        # Define o filtro de data conforme o período escolhido
        if periodo == "mensal":
            filtro_data = "date(data) >= date('now', '-1 month')"
            titulo = "📅 Relatório mensal"

        elif periodo == "trimestral":
            filtro_data = "date(data) >= date('now', '-3 months')"
            titulo = "📅 Relatório trimestral"

        elif periodo == "semestral":
            filtro_data = "date(data) >= date('now', '-6 months')"
            titulo = "📅 Relatório semestral"

        elif periodo == "anual":
            filtro_data = "date(data) >= date('now', '-1 year')"
            titulo = "📅 Relatório anual"

        else:
            await update.message.reply_text(
                "Use assim: /relatorioperiodo mensal\n"
                "Opções: mensal, trimestral, semestral ou anual"
            )
            return

        # Busca os gastos por categoria dentro do período escolhido
        cursor.execute(f'''
            SELECT categoria, SUM(valor)
            FROM gastos
            WHERE user_id = ? AND {filtro_data}
            GROUP BY categoria
            ORDER BY SUM(valor) DESC
        ''', (user_id,))

        gastos = cursor.fetchall()
        conn.close()

        # Se não tiver gasto no período
        if len(gastos) == 0:
            await update.message.reply_text("Nenhum gasto encontrado nesse período.")
            return

        # Soma todos os gastos do período
        total_gasto = sum([g[1] for g in gastos])

        # Monta a mensagem do relatório
        msg = f"{titulo}\n\n"
        msg += f"📉 Total gasto: R${total_gasto:.2f}\n\n"
        msg += "*Gastos por categoria:*\n"

        # Mostra cada categoria
        for categoria, valor in gastos:
            msg += f"• {categoria}: R${valor:.2f}\n"

        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN
        )

    except:
        await update.message.reply_text(
            "Use assim: /relatorioperiodo mensal\n"
            "Opções: mensal, trimestral, semestral ou anual"
        )

# Parte que liga o bot
def main():
    # Cria o banco de dados antes do bot iniciar
    criar_banco()

    # Cria a aplicação do Telegram com o token do bot
    app = Application.builder().token(TOKEN).build()

    
    # Comandos do bot (MAIN)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("salario", salario))
    app.add_handler(CommandHandler("limite", definir_limite))
    app.add_handler(CommandHandler("desativarlimite", desativar_limite))
    app.add_handler(CommandHandler("ativarlimite", ativar_limite))
    app.add_handler(CommandHandler("gasto", registrar_gasto))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("apagar", apagar))
    app.add_handler(CommandHandler("relatorioperiodo", relatorio_periodo))

    # Mensagens sem comando também viram gasto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_gasto))

    # Mostra no terminal que o bot está rodando
    print("Bot rodando... Pressione Ctrl+C para parar.")

    # Inicia o bot
    app.run_polling()


# Faz o programa começar pela função main
if __name__ == '__main__':
    main()