import telebot

bot = telebot.TeleBot('8996493505:AAHKdGUbVC_m004C04n5EkqXEy9AApAfNBc')

@bot.message_handler(['start', 'help'])
def start(msg):
    bot.reply_to(msg, 'Qual categoria você gastou?')

bot.infinity_polling()

def receber_categoria(msg):
    categoria = msg.text
    bot.reply_to(msg, f'Categoria escolhida: {categoria}')

bot.infinity_polling()