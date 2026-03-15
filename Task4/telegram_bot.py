import os
import telebot
from rag import RAGBot


class TelegramRAGBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.rag_bot = RAGBot()
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.reply_to(message,
                "RAG-бот по вселенной Void Chronicles (Star Wars)\n\n"
                "Задавайте вопросы о персонажах, планетах и технологиях."
            )

        @self.bot.message_handler(func=lambda m: True)
        def handle_message(message):
            query = message.text

            try:
                response = self.rag_bot.generate_response(query)

                parts = []
                if response.get("reasoning"):
                    parts.append(f"*Рассуждение:*\n{response['reasoning']}\n")

                parts.append(f"*Ответ:*\n{response['answer']}")

                if response.get("sources"):
                    sources_text = "\n\n*Источники:*"
                    for i, source in enumerate(response["sources"][:3], 1):
                        sources_text += f"\n{i}. `{source['source']}`"
                    parts.append(sources_text)

                result = "\n".join(parts)

                if len(result) > 4096:
                    result = result[:4090] + "..."

                self.bot.reply_to(message, result, parse_mode='Markdown')

            except Exception as e:
                self.bot.reply_to(message, f"Ошибка: {str(e)}")

    def run(self):
        print("Telegram бот запущен...")
        self.bot.infinity_polling()


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Ошибка: установите переменную окружения TELEGRAM_BOT_TOKEN")
        return

    bot = TelegramRAGBot(token)
    bot.run()


if __name__ == "__main__":
    main()
