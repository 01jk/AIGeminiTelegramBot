# Gemini Telegram Bot - Walkthrough

This walkthrough explains how to run and test the bot (Updated for SDK v1.0).

## Prerequisites
1. Ensure `python` is installed.
2. Ensure dependencies are installed: `pip install -r requirements.txt`.
3. Keys are configured in `config.py` (or `.env`).

## Running the Bot
Open a terminal in `d:\Python\gemini\gemini ai` and run:
```bash
python aibot.py
```
*Wait for the message "Bot is running..."*

## Testing Features

| Feature | Action | Expected Result |
| :--- | :--- | :--- |
| **Chat** | Send "Привет". | Bot replies using `gemini-2.0-flash`. |
| **Video** | Send a video. | Bot processes and describes it. |
| **TTS** | Send `/tts Привет`. | Bot sends an **Audio File** (MP3). |

## Troubleshooting
- **Model Errors**: If `gemini-2.0-flash` fails, try `gemini-flash-latest` in `aibot.py`.
- **TTS Errors**: Returns as Audio file to bypass voice message privacy settings.
