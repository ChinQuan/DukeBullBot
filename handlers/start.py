from handlers import price  # upewnij się, że import jest na górze

...

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'price':
        await price.check_price(update, context)
    elif query.data == 'info':
        await price.info(update, context)
    elif query.data == 'spin':
        await spin_game(update, context)
    elif query.data == 'lottery':
        await check_lottery(update, context)
