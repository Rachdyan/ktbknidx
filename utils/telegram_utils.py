import telegram


async def test_bot_access(bot, chat_id):
    """
    Tests if the bot can access and send messages to the specified
    chat/channel.

    Args:
        bot (telegram.Bot): An initialized python-telegram-bot Bot instance.
        chat_id (int | str): The target chat ID to test.

    Returns:
        bool: True if bot can access the chat, False otherwise.
    """
    try:
        # Get bot info first
        bot_info = await bot.get_me()
        bot_id = bot_info.id
        # Try to get chat information
        chat = await bot.get_chat(chat_id)
        print(f"✓ Bot can access chat: {chat.title} (Type: {chat.type})")

        # For channels, check if bot is an admin
        if chat.type in ['channel', 'supergroup']:
            try:
                admins = await bot.get_chat_administrators(chat_id)
                bot_is_admin = any(admin.user.id == bot_id
                                   for admin in admins)
                if bot_is_admin:
                    print(f"✓ Bot is an administrator in {chat.title}")
                else:
                    print(f"✗ Bot is NOT an administrator in {chat.title}")
                    print("  → Add the bot as an admin with "
                          "'Post Messages' permission")
                    return False
            except telegram.error.TelegramError as e:
                print(f"✗ Cannot check admin status: {e}")
                return False

        return True
    except telegram.error.TelegramError as e:
        print(f"✗ Bot cannot access chat {chat_id}: {e}")
        if "chat not found" in str(e).lower():
            print("  → Make sure:")
            print("    1. The chat ID is correct")
            print("    2. The bot has been added to the channel/group")
            print("    3. The bot is an administrator (for channels)")
        return False


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
