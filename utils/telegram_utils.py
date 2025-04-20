import telegram


async def send_summary_message(row_data, bot, chat_id):
    """
    Formats a message from row_data and sends it via the Telegram bot.

    Args:
        row_data (dict | pd.Series): Data containing 'message_string' and
                                     'summary'.
                                      Should support dictionary-style access.
        bot (telegram.Bot): An initialized python-telegram-bot Bot instance.
        chat_id (int | str): The target chat ID to send the message to.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    try:
        # 1. Format the message string from the input data
        message_str = str(row_data['message_string'])  # Ensure string type
        message_str += '\n\n'
        message_str += str(row_data['summary'])     # Ensure string type

        # 2. Attempt to send the formatted message
        print(f"Attempting to send summary message to chat ID: {chat_id}")
        await bot.send_message(
            chat_id=chat_id,
            text=message_str,
            parse_mode='HTML'
        )
        print(f"Summary Message sent successfully to chat ID: {chat_id}!")
        return True

    except telegram.error.TelegramError as e:
        # Handle potential Telegram API errors
        print(f"Telegram Error sending to chat ID {chat_id}: {e}")
        if "chat not found" in str(e).lower():
            print(f"Hint (Chat ID: {chat_id}):"
                  "Make sure the chat ID is correct and the bot "
                  "can send messages to this chat "
                  "(user started bot / bot is admin / etc.).")
        elif "bot was blocked by the user" in str(e).lower():
            print(f"Hint (Chat ID: {chat_id}): "
                  "The target user/chat has blocked this bot.")
        # Add more specific error checks if needed (e.g., message too long)
        return False

    except KeyError as e:
        # Handle cases where 'message_string' or 'summary' is missing
        print(f"Error formatting message for chat ID {chat_id}: "
              f"Missing key {e} in input data.")
        return False

    except Exception as e:
        # Catch any other unexpected errors during the process
        print("An unexpected error occurred while sending to chat ID"
              f"{chat_id}: {e}")
        return False
