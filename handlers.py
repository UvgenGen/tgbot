import base64
import html
import json
import logging
import traceback

from bs4 import BeautifulSoup
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.ext import CallbackContext

import config
from api import get_book_deatils, search_books

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text(
        f"Use /start to test this bot. \n"
        f"Use /search <book_name> to find books."
    )


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    update.message.reply_text("Hi. Use /help for display info")


def search(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    books = search_books(context.args)
    logger.info(f'found books {len(books)} by "{context.args}"')
    if books:
        keyboard = []
        url_dict = {}
        for i, book in enumerate(books):
            text=f"{book.get('name')} - {', '.join(book.get('authors'))}"
            keyboard.append(
                [InlineKeyboardButton(text, callback_data=i)]
            )
            url_dict.update({i: book.get('url')})

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_html((
            f"Found books ({len(books)}): "
            f"<a href='tg://ntelebot/{base64.b64encode(json.dumps(url_dict).encode()).decode()}'>\u200b</a>"
            ),
            reply_markup=reply_markup)
    else:
        update.message.reply_text('Books not found...')


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    soup = BeautifulSoup(query.message.text_html, 'html.parser')
    url_dict = json.loads(base64.b64decode(soup.a['href'].replace('tg://ntelebot/', '')))
    datails_data = get_book_deatils(url_dict[query.data])
    keyboard = [[InlineKeyboardButton(download_urls.get('text'), url=download_urls.get('url'))] for download_urls in datails_data.get('download_urls')]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=datails_data.get('name'), reply_markup=reply_markup)


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=config.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
