🫧 Whisper Chat – Anonymous Telegram Chat Bot

Whisper Chat is an anonymous one-to-one Telegram chat bot that connects users randomly while preserving privacy.
No usernames, no profiles — just pure conversation.

🚀 Features

🔐 Anonymous Chat – No personal info shared

🔄 Any ↔ Any Matching with gender-based bias

👤 Gender Selection (Male / Female / Other)

🎂 Age Setting & Update

🔞 NSFW Control

Male: NSFW allowed by default

Female / Other: NSFW disabled by default (opt-in)

🚨 Report & Exit Chat

🔁 Next Chat Button (no need to go back to menu)

⚙️ Settings Menu

💾 Persistent Database (SQLite)

🇮🇳 Country preset: India

🤖 Built with python-telegram-bot

🧠 How It Works

User starts the bot with /start

Selects gender

(Optional) Sets age in settings

Uses /find to get matched

Messages are relayed anonymously

Chat can be ended anytime

User can instantly start a Next Chat

🛠 Tech Stack
Component	Technology
Language	Python 3.11
Telegram API	python-telegram-bot v20.7
Database	SQLite
Hosting	Local / Cloud (Koyeb, Deta, etc.)
Architecture	Async, event-driven
📁 Project Structure
whisper_chat/
│
├── bot.py                # Main bot logic
├── database_utils.py     # Database helper functions
├── whisper_chat.db       # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation

⚙️ Installation (Local Setup)
1️⃣ Clone the repository
git clone https://github.com/your-username/whisper-chat-bot.git
cd whisper-chat-bot

2️⃣ Create & activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Set bot token (environment variable)
set BOT_TOKEN=your_telegram_bot_token   # Windows

5️⃣ Run the bot
python bot.py

🤖 Bot Commands
Command	Description
/start	Start the bot
/find	Find a chat partner
/stop	End current chat
/settings	Change age or gender
/status	View profile settings
/help	Show help menu
🚨 Report System

Users can report inappropriate behavior

Reported user chat is immediately terminated

Report count is stored in the database

System is ready for auto-ban extension

🔐 Privacy & Safety

No usernames or profile info shared

Only Telegram user ID is stored

Messages are not logged

User data is minimal and local

📌 Limitations

Free hosting platforms may sleep

SQLite is suitable for small to medium usage

Not designed for large-scale public deployment

🧩 Future Improvements

🚫 Auto-ban after multiple reports

📊 Admin dashboard

🌍 Country-based matching

⭐ Chat rating system

🗄 PostgreSQL database support

🎓 Academic Use

This project is suitable for:

College mini-project

Python development practice

Telegram bot learning

Cloud deployment demonstrations

👤 Author

Name: Atharva Ronghe
Project: Whisper Chat – Anonymous Telegram Bot

📜 License

This project is for educational purposes.
Feel free to modify and extend.


