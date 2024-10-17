from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import sqlite3

def create_table():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            username TEXT,
            subject TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_info(user_info):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (username, subject, description)
        VALUES (?, ?, ?)
    ''', user_info)
    conn.commit()
    conn.close()

def get_matches(subject):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, subject, description
        FROM students
        WHERE subject = ?
    ''', (subject,))
    matches = cursor.fetchall()
    conn.close()
    return matches

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Upload Info"), KeyboardButton("Search Students")]
    ]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Welcome to the study body bot!\n\n"
        "Please choose an option:",
        reply_markup=markup
    )
    return UPLOAD_INFO

async def upload_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == "Upload Info":
        await update.message.reply_text(
            "Please enter your telegram username (e.g. @username):"
        )
        return USERNAME
    elif user_choice == "Search Students":
        await update.message.reply_text(
            "Please enter your subject in lower-case (e.g. eap, math, leadership):",
            reply_markup=ForceReply(selective=True)
        )
        return SUBJECT_PREF

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data["username"] = username

    await update.message.reply_text(
        "Please enter your subject in lower-case (e.g. eap, math, leadership):"
    )
    return SUBJECT_INPUT

async def subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subject = update.message.text
    context.user_data["subject"] = subject

    await update.message.reply_text(
        "Please enter a short description about yourself:"
    )
    return DESCRIPTION_INPUT

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description = update.message.text
    context.user_data["description"] = description

    user_info = (
        context.user_data.get("username"),
        context.user_data.get("subject"),
        context.user_data.get("description")
    )
    save_user_info(user_info)

    context.user_data.clear()

    return await start(update, context)

async def subject_pref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subject = update.message.text
    matches = get_matches(subject)

    if matches:
        await update.message.reply_text("Here are your matches:")
        for match in matches:
            username, subject, description = match
            message = f"Username: {username}\nSubject: {subject}\nDescription: {description}\n"
            await update.message.reply_text(message)
    else:
        await update.message.reply_text("Sorry, no matches found.")

    context.user_data.clear()

    return ConversationHandler.END

USERNAME, SUBJECT_INPUT, DESCRIPTION_INPUT, SUBJECT_PREF, UPLOAD_INFO = range(5)

def main():
    create_table()
    
    application = Application.builder().token("6415075805:AAG7VWPMPVpC7Sll2dU4TgVaFYRIFwbbnC8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT, username)],
            SUBJECT_INPUT: [MessageHandler(filters.TEXT, subject)],
            DESCRIPTION_INPUT: [MessageHandler(filters.TEXT, description)],
            SUBJECT_PREF: [MessageHandler(filters.TEXT, subject_pref)],
            UPLOAD_INFO: [MessageHandler(filters.TEXT, upload_info)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
