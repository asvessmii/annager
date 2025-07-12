#!/usr/bin/env python3
"""
Backend Test Suite for Telegram Bot Annaager
Tests database functionality, admin logic, and bot structure
"""

import sys
import os
import sqlite3
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock
import asyncio

# Add the app directory to Python path
sys.path.insert(0, '/app')

import db
import bot

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []
    
    def run_test(self, test_name, test_func):
        self.tests_run += 1
        try:
            result = test_func()
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            self.tests_passed += 1
            print(f"✅ {test_name}")
            return True
        except Exception as e:
            self.failures.append(f"{test_name}: {str(e)}")
            print(f"❌ {test_name}: {str(e)}")
            return False
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        if self.failures:
            print(f"\nFAILURES:")
            for failure in self.failures:
                print(f"  - {failure}")
        print(f"{'='*60}")

def test_database_initialization():
    """Test database initialization and table structure"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        # Initialize database
        db.init_db()
        
        # Check if tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = ['users', 'messages', 'buttons']
        for table in required_tables:
            if table not in tables:
                raise Exception(f"Required table '{table}' not found")
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['id', 'current_question', 'score', 'completed', 'last_result']
        for col in required_columns:
            if col not in columns:
                raise Exception(f"Required column '{col}' not found in users table")
        
        conn.close()
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_no_duplicate_buttons():
    """Test that there are no duplicate buttons in the database"""
    conn = sqlite3.connect(db.DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check for duplicates
    cursor.execute("""
        SELECT message_id, text, url, callback_data, COUNT(*) as count 
        FROM buttons 
        GROUP BY message_id, text, COALESCE(url, ''), COALESCE(callback_data, '') 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    conn.close()
    
    if duplicates:
        raise Exception(f"Found {len(duplicates)} duplicate button groups")
    
    return True

def test_user_progress_logic():
    """Test user progress tracking and completion logic"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        db.init_db()
        
        # Test user creation
        test_user_id = 12345
        db.create_user(test_user_id)
        
        user_data = db.get_user_data(test_user_id)
        if not user_data:
            raise Exception("User not created properly")
        
        if user_data[1] != 0 or user_data[2] != 0 or user_data[3] != 0:
            raise Exception("User initial state incorrect")
        
        # Test progress update
        db.update_user_progress(test_user_id, 2, 50)
        user_data = db.get_user_data(test_user_id)
        if user_data[1] != 2 or user_data[2] != 50:
            raise Exception("User progress update failed")
        
        # Test completion
        db.complete_user_test(test_user_id, 150, "Test result")
        user_data = db.get_user_data(test_user_id)
        if user_data[3] != 1 or user_data[4] != "Test result":
            raise Exception("User test completion failed")
        
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_admin_users_function():
    """Test admin users display logic"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        db.init_db()
        
        # Create test users with different states
        # User 1: Not started
        db.create_user(11111)
        
        # User 2: In progress
        db.create_user(22222)
        db.update_user_progress(22222, 3, 80)
        
        # User 3: Completed
        db.create_user(33333)
        db.complete_user_test(33333, 180, "90%: Test result")
        
        # Get all users
        users = db.get_all_users()
        if len(users) != 3:
            raise Exception(f"Expected 3 users, got {len(users)}")
        
        # Check user states
        user_states = {user[0]: user for user in users}
        
        # User 1 should be not started
        user1 = user_states[11111]
        if user1[1] != 0 or user1[2] != 0 or user1[3] != 0:
            raise Exception("User 1 state incorrect")
        
        # User 2 should be in progress
        user2 = user_states[22222]
        if user2[1] != 3 or user2[2] != 80 or user2[3] != 0:
            raise Exception("User 2 state incorrect")
        
        # User 3 should be completed
        user3 = user_states[33333]
        if user3[3] != 1 or user3[4] != "90%: Test result":
            raise Exception("User 3 state incorrect")
        
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_message_management():
    """Test message CRUD operations"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        db.init_db()
        
        # Test adding message
        db.add_message("test_msg", "Test message content", None)
        
        # Test retrieving message
        message_data = db.get_message("test_msg")
        if not message_data or message_data[0] != "Test message content":
            raise Exception("Message retrieval failed")
        
        # Test updating message
        db.update_message_text("test_msg", "Updated message content")
        message_data = db.get_message("test_msg")
        if message_data[0] != "Updated message content":
            raise Exception("Message update failed")
        
        # Test getting all messages
        all_messages = db.get_all_messages()
        test_messages = [msg for msg in all_messages if msg[0] == "test_msg"]
        if len(test_messages) != 1:
            raise Exception("Get all messages failed")
        
        # Test deleting message
        db.delete_message("test_msg")
        message_data = db.get_message("test_msg")
        if message_data:
            raise Exception("Message deletion failed")
        
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_button_management():
    """Test button CRUD operations"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        db.init_db()
        
        # Add a message first
        db.add_message("test_msg", "Test message", None)
        
        # Test adding button
        db.add_button("test_msg", "Test Button", "https://example.com", None)
        
        # Test retrieving buttons for message
        buttons = db.get_buttons_for_message("test_msg")
        if len(buttons) != 1 or buttons[0][0] != "Test Button":
            raise Exception("Button retrieval failed")
        
        # Test getting all buttons
        all_buttons = db.get_all_buttons()
        test_buttons = [btn for btn in all_buttons if btn[1] == "test_msg"]
        if len(test_buttons) != 1:
            raise Exception("Get all buttons failed")
        
        # Test updating button
        button_id = test_buttons[0][0]
        db.update_button(button_id, new_text="Updated Button")
        
        buttons = db.get_buttons_for_message("test_msg")
        if buttons[0][0] != "Updated Button":
            raise Exception("Button update failed")
        
        # Test deleting button
        db.delete_button(button_id)
        buttons = db.get_buttons_for_message("test_msg")
        if len(buttons) != 0:
            raise Exception("Button deletion failed")
        
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_bot_constants_and_structure():
    """Test bot constants and basic structure"""
    # Check BOT_TOKEN is set
    if not bot.BOT_TOKEN or bot.BOT_TOKEN == "YOUR_BOT_TOKEN":
        raise Exception("BOT_TOKEN not properly configured")
    
    # Check ADMIN_ID is set
    if not bot.ADMIN_ID or bot.ADMIN_ID == 0:
        raise Exception("ADMIN_ID not properly configured")
    
    # Check QUESTIONS structure
    if not bot.QUESTIONS or len(bot.QUESTIONS) == 0:
        raise Exception("QUESTIONS not properly defined")
    
    # Verify each question has required structure
    for q_num, question in bot.QUESTIONS.items():
        if 'text' not in question or 'options' not in question:
            raise Exception(f"Question {q_num} missing required fields")
        
        if not question['options'] or len(question['options']) == 0:
            raise Exception(f"Question {q_num} has no options")
    
    # Check RESULTS structure
    if not bot.RESULTS or len(bot.RESULTS) == 0:
        raise Exception("RESULTS not properly defined")
    
    return True

async def test_admin_panel_access():
    """Test admin panel access control"""
    # Mock update and context
    update = Mock()
    context = Mock()
    
    # Test admin access
    update.effective_user.id = bot.ADMIN_ID
    update.message.reply_text = AsyncMock()
    
    result = await bot.admin_panel(update, context)
    
    # Should return ADMIN_MENU state
    if result != bot.ADMIN_MENU:
        raise Exception("Admin panel access failed for admin user")
    
    # Test non-admin access
    update.effective_user.id = 99999  # Different ID
    update.message.reply_text = AsyncMock()
    
    result = await bot.admin_panel(update, context)
    
    # Should return ConversationHandler.END
    from telegram.ext import ConversationHandler
    if result != ConversationHandler.END:
        raise Exception("Admin panel should deny access to non-admin users")
    
    return True

def test_clean_duplicate_buttons_function():
    """Test the clean_duplicate_buttons function"""
    # Create temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    original_db = db.DATABASE_NAME
    db.DATABASE_NAME = temp_db
    
    try:
        # Initialize database without populate_initial_messages
        conn = sqlite3.connect(temp_db)
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
        conn.commit()
        
        # Add a message
        cursor.execute("INSERT INTO messages (message_id, text, photo_path) VALUES (?, ?, ?)", 
                      ("test_msg", "Test message", None))
        
        # Insert duplicate buttons manually
        cursor.execute("INSERT INTO buttons (message_id, text, url, callback_data) VALUES (?, ?, ?, ?)", 
                      ("test_msg", "Duplicate Button", "https://example.com", None))
        cursor.execute("INSERT INTO buttons (message_id, text, url, callback_data) VALUES (?, ?, ?, ?)", 
                      ("test_msg", "Duplicate Button", "https://example.com", None))
        cursor.execute("INSERT INTO buttons (message_id, text, url, callback_data) VALUES (?, ?, ?, ?)", 
                      ("test_msg", "Unique Button", "https://example2.com", None))
        
        conn.commit()
        conn.close()
        
        # Check we have 3 buttons
        all_buttons = db.get_all_buttons()
        if len(all_buttons) != 3:
            raise Exception(f"Expected 3 buttons before cleanup, got {len(all_buttons)}")
        
        # Clean duplicates
        deleted_count = db.clean_duplicate_buttons()
        
        if deleted_count != 1:
            raise Exception(f"Expected to delete 1 duplicate, deleted {deleted_count}")
        
        # Check we now have 2 buttons
        all_buttons = db.get_all_buttons()
        if len(all_buttons) != 2:
            raise Exception(f"Expected 2 buttons after cleanup, got {len(all_buttons)}")
        
        return True
        
    finally:
        db.DATABASE_NAME = original_db
        if os.path.exists(temp_db):
            os.remove(temp_db)

def main():
    """Run all tests"""
    print("🤖 Starting Telegram Bot Annaager Backend Tests")
    print("="*60)
    
    results = TestResults()
    
    # Database tests
    print("\n📊 DATABASE TESTS")
    results.run_test("Database Initialization", test_database_initialization)
    results.run_test("No Duplicate Buttons", test_no_duplicate_buttons)
    results.run_test("User Progress Logic", test_user_progress_logic)
    results.run_test("Admin Users Function", test_admin_users_function)
    results.run_test("Message Management", test_message_management)
    results.run_test("Button Management", test_button_management)
    results.run_test("Clean Duplicate Buttons", test_clean_duplicate_buttons_function)
    
    # Bot structure tests
    print("\n🤖 BOT STRUCTURE TESTS")
    results.run_test("Bot Constants and Structure", test_bot_constants_and_structure)
    results.run_test("Admin Panel Access Control", test_admin_panel_access)
    
    results.print_summary()
    
    # Return exit code based on test results
    return 0 if results.tests_passed == results.tests_run else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)