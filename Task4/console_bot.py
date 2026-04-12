from rag import RAGBot


class ConsoleBot:
    def __init__(self):
        self.rag_bot = RAGBot()

    def format_response(self, response):
        parts = []

        if response.get("reasoning"):
            parts.append(f"Рассуждение:\n{response['reasoning']}\n")

        parts.append(f"Ответ:\n{response['answer']}")

        if response.get("sources"):
            parts.append("\nИсточники:")
            for i, source in enumerate(response["sources"], 1):
                parts.append(f"  {i}. {source['source']}")

        return "\n".join(parts)

    def run(self):
        print("\nRAG-бот по вселенной Void Chronicles")
        print("Введите 'exit' для выхода\n")

        while True:
            try:
                query = input("Вопрос: ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit']:
                    break

                response = self.rag_bot.generate_response(query)
                result = self.format_response(response)
                print(f"\n{result}\n")
                print("-" * 60 + "\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}\n")


def main():
    bot = ConsoleBot()
    bot.run()


if __name__ == "__main__":
    main()
