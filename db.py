import sqlite3

DATABASE_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            current_question INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            last_result TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            text TEXT,
            photo_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buttons (
            button_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT,
            text TEXT,
            url TEXT,
            callback_data TEXT,
            FOREIGN KEY (message_id) REFERENCES messages (message_id)
        )
    """)
    
    # Add new columns if they don't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN completed INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_result TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()
    populate_initial_messages()

def populate_initial_messages():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM messages")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    messages_data = [
        ("message_1", "Привет! Ты попала в мой бот\n\nМеня зовут Анна Герц\n\nЯ натуропат, помогаю тысячам женщин становиться здоровыми и стройными и влюбляться в свое тело вновь, и вновь.\n\nВ этом боте будет много полезных гайдов и уроков 😍\n\nПрисоединяйся👍", "/home/ubuntu/upload/image.png"),
        ("message_2", "Для начала тебе нужно подписаться на мой телеграм-канал, в котором я делюсь очень полезной информацией о чистоте питания, тела и сознания. Показываю реальную жизнь без перекосов, категоричности и вылизанной картинки идеальной жизни !\n\nГде и ты, и я имеем право на ошибки в питании, в спорте, в мыслях, в отношениях - но в этой неидеальности и есть жизнь👍\n\nА также ты найдешь там полезные посты и подкасты про питание и не только — материал, который не знает гугл, так как это мой опыт и опыт 1000 женщин, прошедших путь очищения со мной .\n\nПодписывайся и жми кнопку ниже ⬇️", None),
        ("message_3", "Вижу подписку 💗", None),
        ("message_4", "Если тебе 30+, а вес стоит, цикл скачет, отеки, лицо \"плывёт\".\n\nЭто может быть следствием недостаточного потребления белка, отсутствием полезных жиров, застоем лимфы, признаками состояния непроходящего стресса и высокого уровня кортизола, невниманием к себе и своему телу, и пр.\n\nЯ сделала короткий тест (5 вопросов) чтобы показать:\n\nкак сейчас работают твои гормоны\n\nподойдёт ли тебе кето\n\nи что будет, если ты попробуешь вычистить свое тело 👍\n\nПосле теста, я выдам тебе результат и рацион, адаптированный под твою ситуацию", None),
        ("test_intro", "📍Заголовок:\n\nОтветь на 5 вопросов — и я пришлю твой результат + адаптированный рацион на 3 дня", None)
    ]

    buttons_data = [
        ("message_2", "Подписаться на канал", "https://t.me/your_channel_link", None),
        ("message_2", "Проверка подписки", None, "check_subscription"),
        ("message_4", "Пройти тест →", None, "start_test")
    ]

    for msg_id, text, photo_path in messages_data:
        cursor.execute("INSERT INTO messages (message_id, text, photo_path) VALUES (?, ?, ?)", (msg_id, text, photo_path))
    
    for msg_id, text, url, callback_data in buttons_data:
        cursor.execute("INSERT INTO buttons (message_id, text, url, callback_data) VALUES (?, ?, ?, ?)", (msg_id, text, url, callback_data))
    
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, current_question, score, completed, last_result FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def create_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, current_question, score, completed, last_result) VALUES (?, 0, 0, 0, NULL)", (user_id,))
    conn.commit()
    conn.close()

def update_user_progress(user_id, question_num, score):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET current_question = ?, score = ? WHERE id = ?", (question_num, score, user_id))
    conn.commit()
    conn.close()

def reset_user_progress(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET current_question = 0, score = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def complete_user_test(user_id, final_score, result_text):
    """Mark user test as completed with final score and result"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET completed = 1, score = ?, last_result = ?, current_question = 0 WHERE id = ?", 
                   (final_score, result_text, user_id))
    conn.commit()
    conn.close()

def get_message(message_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT text, photo_path FROM messages WHERE message_id = ?", (message_id,))
    message_data = cursor.fetchone()
    conn.close()
    return message_data

def get_buttons_for_message(message_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT text, url, callback_data FROM buttons WHERE message_id = ?", (message_id,))
    buttons_data = cursor.fetchall()
    conn.close()
    return buttons_data

def get_all_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, current_question, score, completed, last_result FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def update_message_text(message_id, new_text):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET text = ? WHERE message_id = ?", (new_text, message_id))
    conn.commit()
    conn.close()

def update_button(button_id, new_text=None, new_url=None, new_callback_data=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    updates = []
    params = []
    if new_text is not None:
        updates.append("text = ?")
        params.append(new_text)
    if new_url is not None:
        updates.append("url = ?")
        params.append(new_url)
    if new_callback_data is not None:
        updates.append("callback_data = ?")
        params.append(new_callback_data)
    
    if updates:
        query = f"UPDATE buttons SET {', '.join(updates)} WHERE button_id = ?"
        params.append(button_id)
        cursor.execute(query, tuple(params))
        conn.commit()
    conn.close()

def add_button(message_id, text, url=None, callback_data=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO buttons (message_id, text, url, callback_data) VALUES (?, ?, ?, ?)", (message_id, text, url, callback_data))
    conn.commit()
    conn.close()

def delete_button(button_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM buttons WHERE button_id = ?", (button_id,))
    conn.commit()
    conn.close()




def get_all_messages():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT message_id, text, photo_path FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return messages

def clean_duplicate_buttons():
    """Remove duplicate buttons based on message_id, text, url, and callback_data"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Find duplicates and keep only the first occurrence
    cursor.execute("""
        DELETE FROM buttons 
        WHERE button_id NOT IN (
            SELECT MIN(button_id) 
            FROM buttons 
            GROUP BY message_id, text, COALESCE(url, ''), COALESCE(callback_data, '')
        )
    """)
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def get_all_buttons():
    """Get all buttons with their message information"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.button_id, b.message_id, b.text, b.url, b.callback_data, m.text as message_text
        FROM buttons b
        LEFT JOIN messages m ON b.message_id = m.message_id
        ORDER BY b.message_id, b.button_id
    """)
    buttons = cursor.fetchall()
    conn.close()
    return buttons

def add_message(message_id, text, photo_path=None):
    """Add a new message"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (message_id, text, photo_path) VALUES (?, ?, ?)", 
                   (message_id, text, photo_path))
    conn.commit()
    conn.close()

def delete_message(message_id):
    """Delete a message and all its buttons"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Delete associated buttons first
    cursor.execute("DELETE FROM buttons WHERE message_id = ?", (message_id,))
    # Delete the message
    cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_button_by_id(button_id):
    """Get button details by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT button_id, message_id, text, url, callback_data FROM buttons WHERE button_id = ?", (button_id,))
    button = cursor.fetchone()
    conn.close()
    return button




