from telegram.parsemode import ParseMode
import app_config
from telegram import Bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def send_telegram_message(message, article_url, comment_url):
    bot = Bot(token=app_config.bot_token)
    keyboard = [
        [
            InlineKeyboardButton(
                "Article",
                url=article_url,
            ),
            InlineKeyboardButton(
                "Comments",
                url=comment_url,
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(
        chat_id=app_config.telegram_chat_id,
        text=message,
        disable_web_page_preview=False,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )
