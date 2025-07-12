import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
import db

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Replace with your actual bot token and admin ID
BOT_TOKEN = "8025187931:AAGsFR7T7rDU0ati-Mo3wMR4BBBzFr6caNM"
ADMIN_ID = 7470811680

# Test questions and options
QUESTIONS = {
    1: {
        "text": "Твой возраст",
        "options": {
            "до 30": 20,
            "30–35": 30,
            "36–40": 40,
            "41–45": 50,
            "46+": 60
        }
    },
    2: {
        "text": "Как у тебя с гормонами?",
        "options": {
            "Всё стабильно": 20,
            "ПМС усилился, отёки, раздражение": 40,
            "Начались сбои, прыгает цикл": 50,
            "Уже менопауза / близко": 60
        }
    },
    3: {
        "text": "Как ты сейчас питаешься?",
        "options": {
            "ЗОЖ, но вес не уходит": 40,
            "Часто срывы": 30,
            "Постоянно голодная": 50,
            "Ем нормально, но тяжесть": 50
        }
    },
    4: {
        "text": "Что больше всего бесит?",
        "options": {
            "Лицо стало \"пухлым\"": 40,
            "Вес держится на животе": 50,
            "Сил нет": 50,
            "Постоянные перепады в настроении": 50,
            "Падает либидо": 40,
            "Всё вместе 😩": 60
        }
    },
    5: {
        "text": "Пробовала ли ты кето раньше?",
        "options": {
            "Да, но не зашло": 20,
            "Никогда": 30,
            "Хочу, но боюсь": 40,
            "Пробовала — понравилось": 60
        }
    }
}

RESULTS = [
    (100, 130, "60%: “Кето тебе подойдёт ! Оно будет тебе полезно для профилактики гормональных сбоев и стабилизации веса."),
    (131, 170, "70%: “Есть хорошие показания, самое главное - мягкий вход . Лови рацион на 3 дня ! |"),
    (171, 200, "80%: “Кето отлично подойдёт — твои симптомы указывают на инсулинорезистентность и дефицит жиров.”"),
    (201, 230, "90%: “Тебе прямой путь на женское кето. Организм просит перезапуска.”"),
    (231, float("inf"), "100%: “У тебя почти классическая картина ‘гормональной усталости’. Кето + интервальное питание = 🔥")
]

# States for admin panel conversation
(ADMIN_MENU, ADMIN_USERS, ADMIN_MESSAGES, ADMIN_BUTTONS, ADMIN_TESTS,
 EDIT_MESSAGE_TEXT, EDIT_MESSAGE_PHOTO, EDIT_BUTTON_TEXT, EDIT_BUTTON_URL, EDIT_BUTTON_CALLBACK,
 ADD_MESSAGE_ID, ADD_MESSAGE_TEXT, ADD_MESSAGE_PHOTO, DELETE_MESSAGE_CONFIRM,
 ADD_BUTTON_MESSAGE, ADD_BUTTON_TEXT, ADD_BUTTON_TYPE, ADD_BUTTON_URL, ADD_BUTTON_CALLBACK, DELETE_BUTTON_CONFIRM,
 EDIT_QUESTION_NUM, EDIT_QUESTION_TEXT, EDIT_OPTION_TEXT, EDIT_OPTION_SCORE) = range(22)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and the initial photo."""
    user_id = update.effective_user.id
    db.create_user(user_id)

    message_data = db.get_message("message_1")
    if message_data:
        text, photo_path = message_data
        if photo_path:
            await update.message.reply_photo(photo=photo_path, caption=text)
        else:
            await update.message.reply_text(text)

    await send_message_from_db("message_2", update.message)

async def send_message_from_db(message_id: str, message_obj) -> None:
    message_data = db.get_message(message_id)
    buttons_data = db.get_buttons_for_message(message_id)

    if message_data:
        text, photo_path = message_data
        keyboard = []
        for btn_text, btn_url, btn_callback_data in buttons_data:
            if btn_url:
                keyboard.append([InlineKeyboardButton(btn_text, url=btn_url)])
            elif btn_callback_data:
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=btn_callback_data)])
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        if photo_path:
            await message_obj.reply_photo(photo=photo_path, caption=text, reply_markup=reply_markup)
        else:
            await message_obj.reply_text(text, reply_markup=reply_markup)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the subscription check button."""
    query = update.callback_query
    await query.answer()
    # For now, always positive result as per TZ
    message_data = db.get_message("message_3")
    if message_data:
        text, _ = message_data
        await query.edit_message_text(text)
    await send_message_from_db("message_4", query.message)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /admin command."""
    if update.effective_user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("💬 Сообщения", callback_data="admin_messages")],
            [InlineKeyboardButton("🔘 Кнопки", callback_data="admin_buttons")],
            [InlineKeyboardButton("📝 Тесты", callback_data="admin_tests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = "🔧 Добро пожаловать в админ-панель!\n\nВыберите раздел для управления:"
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return ADMIN_MENU
    else:
        await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
        return ConversationHandler.END

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    users = db.get_all_users()
    response_text = "👥 Список пользователей и их результаты тестов:\n\n"
    if users:
        for user_id, current_question, score, completed, last_result in users:
            if completed:
                status = "✅ Тест пройден"
                result_text = last_result if last_result else "Результат не сохранен"
                progress = f"Баллы: {score}"
            elif current_question > 0:
                status = f"📝 В процессе (вопрос {current_question}/{len(QUESTIONS)})"
                result_text = "Тест не завершен"
                progress = f"Текущие баллы: {score}"
            else:
                status = "❌ Тест не начат"
                result_text = "Тест не пройден"
                progress = "Баллы: 0"
            
            response_text += f"👤 ID: {user_id}\n"
            response_text += f"📊 Статус: {status}\n"
            response_text += f"🎯 {progress}\n"
            response_text += f"📋 Результат: {result_text}\n"
            response_text += "─" * 30 + "\n\n"
    else:
        response_text += "Пользователи не найдены."
    
    # Split message if it's too long
    if len(response_text) > 4000:
        response_text = response_text[:4000] + "\n\n... (список обрезан)"
    
    await query.edit_message_text(response_text)
    return ADMIN_MENU

async def admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    messages = db.get_all_messages()
    keyboard = []
    response_text = "Список сообщений:\n\n"
    if messages:
        for msg_id, text, _ in messages:
            response_text += f"ID: {msg_id}, Текст: {text[:50]}...\n"
            keyboard.append([InlineKeyboardButton(f"Редактировать {msg_id}", callback_data=f"admin_edit_message_{msg_id}")])
    else:
        response_text += "Сообщения не найдены."
    keyboard.append([InlineKeyboardButton("Добавить сообщение", callback_data="admin_add_message")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(response_text, reply_markup=reply_markup)
    return ADMIN_MENU

async def admin_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    message_id = query.data.replace("admin_edit_message_", "")
    context.user_data["editing_message_id"] = message_id
    message_data = db.get_message(message_id)
    if message_data:
        text, _ = message_data
        await query.edit_message_text(f"Введите новый текст для сообщения {message_id}:\n\nТекущий текст:\n{text}")
        return EDIT_MESSAGE_TEXT
    else:
        await query.edit_message_text("Сообщение не найдено.")
        return ADMIN_MENU

async def receive_edited_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_id = context.user_data.get("editing_message_id")
    if message_id:
        new_text = update.message.text
        db.update_message_text(message_id, new_text)
        del context.user_data["editing_message_id"]
        await update.message.reply_text(f"Текст сообщения {message_id} обновлен.")
        # Go back to admin messages menu
        messages = db.get_all_messages()
        keyboard = []
        response_text = "Список сообщений:\n\n"
        if messages:
            for msg_id, text, _ in messages:
                response_text += f"ID: {msg_id}, Текст: {text[:50]}...\n"
                keyboard.append([InlineKeyboardButton(f"Редактировать {msg_id}", callback_data=f"admin_edit_message_{msg_id}")])
        else:
            response_text += "Сообщения не найдены."
        keyboard.append([InlineKeyboardButton("Добавить сообщение", callback_data="admin_add_message")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        return ADMIN_MENU
    else:
        await update.message.reply_text("Ошибка: не удалось определить сообщение для редактирования.")
        return ADMIN_MENU

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the test."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db.reset_user_progress(user_id)
    message_data = db.get_message("test_intro")
    if message_data:
        text, _ = message_data
        await query.edit_message_text(text)
    await send_question(query.message, context, user_id)

async def send_question(message, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    user_data = db.get_user_data(user_id)
    current_question_num = user_data[1] + 1 # current_question is 0-indexed in DB

    if current_question_num > len(QUESTIONS):
        await send_result(message, context, user_id)
        return

    question = QUESTIONS[current_question_num]
    keyboard = []
    for option_text, score_value in question["options"].items():
        keyboard.append([InlineKeyboardButton(option_text, callback_data=f"q_{current_question_num}_{score_value}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(f"Вопрос {current_question_num}: {question['text']}", reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = db.get_user_data(user_id)
    current_question_num = user_data[1]
    current_score = user_data[2]

    callback_data = query.data.split("_")
    question_answered = int(callback_data[1])
    score_gained = int(callback_data[2])

    if question_answered == current_question_num + 1: # Ensure user answers the current question
        new_score = current_score + score_gained
        db.update_user_progress(user_id, current_question_num + 1, new_score)
        await send_question(query.message, context, user_id)
    else:
        await query.edit_message_text("Пожалуйста, ответьте на текущий вопрос.")

async def send_result(message, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    user_data = db.get_user_data(user_id)
    final_score = user_data[2]

    result_message = ""
    for min_score, max_score, text in RESULTS:
        if min_score <= final_score <= max_score:
            result_message = text
            break
    
    await message.reply_text(f"Ваш результат: {final_score} баллов.\n\n{result_message}")
    # Mark test as completed instead of resetting progress
    db.complete_user_test(user_id, final_score, result_message)

def main() -> None:
    """Start the bot."""
    db.init_db() # Initialize the database
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADMIN_MENU: [
                CallbackQueryHandler(admin_users, pattern="^admin_users$"),
                CallbackQueryHandler(admin_messages, pattern="^admin_messages$"),
            ],
            EDIT_MESSAGE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edited_message_text)],
        },
        fallbacks=[CommandHandler("admin", admin_panel)], # Allow re-entering admin panel
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(admin_edit_message, pattern="^admin_edit_message_.*"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern="^q_\d+_\d+$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start)) # Fallback for any text message

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


