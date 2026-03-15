from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import requests


class RAGBot:
    def __init__(
        self,
        chroma_db_path: str = "../Task3/chroma_db",
        collection_name: str = "void_chronicles_knowledge",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        ollama_model: str = "qwen2.5",
        ollama_url: str = "http://localhost:11434"
    ):
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        self.vectorstore = Chroma(
            persist_directory=chroma_db_path,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )

    def retrieve_context(self, query: str) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=3)

    def build_system_prompt(self) -> str:
        return """Ты помощник по вселенной Void Chronicles. Отвечай на вопросы используя предоставленный контекст.

ВАЖНО: Весь твой ответ должен быть ТОЛЬКО на русском языке. Никогда не используй китайский, английский или другие языки в ответе.

Используй Chain-of-Thought:
1. Проанализируй вопрос
2. Найди информацию в контексте
3. Сформулируй ответ

Формат ответа:
Рассуждение: [твои шаги на РУССКОМ]
Ответ: [финальный ответ на РУССКОМ]

Правила:
- Отвечай только на основе контекста
- Если информации нет, ответь: 'Я не знаю. В моей базе знаний нет информации по этому вопросу.'
- Весь ответ СТРОГО на русском языке"""

    def build_user_prompt(self, query: str, context_docs: List[Document]) -> str:
        few_shot_examples = [
            {
                "question": "Кто такой Drake Vex?",
                "context": "[Han_Solo.txt] Drake Vex is a fictional character in the Star Wars franchise. In the original trilogy, Solo and his Wookiee friend Chewbacca are smugglers who join the Rebel Alliance and fight against the Galactic Empire.",
                "answer": "Drake Vex — вымышленный персонаж франшизы Star Wars. В оригинальной трилогии он контрабандист, который вместе со своим другом-вуки Чубаккой присоединяется к Альянсу повстанцев и сражается против Галактической Империи."
            },
            {
                "question": "Что такое Nexus Hawk?",
                "context": "[Millennium_Falcon.txt] The Millennium Falcon is a YT-1300 Corellian light freighter, primarily commanded by smuggler Han Solo and his Wookiee first mate, Chewbacca. Described as one of the fastest vessels in the Star Wars canon.",
                "answer": "Nexus Hawk (Millennium Falcon) — это легкий грузовой корабль YT-1300, которым командует контрабандист Хан Соло и его помощник-вуки Чубакка. Описывается как один из самых быстрых кораблей в каноне Star Wars."
            }
        ]

        parts = ["Примеры:\n"]
        for ex in few_shot_examples:
            parts.append(f"Q: {ex['question']}\nКонтекст: {ex['context']}\nA: {ex['answer']}\n")

        parts.append("Контекст:")
        for doc in context_docs:
            parts.append(f"\n[{doc.metadata.get('source', 'unknown')}]")
            parts.append(doc.page_content)

        parts.append(f"\nВопрос: {query}")

        return "\n".join(parts)

    def generate_response(self, query: str) -> Dict:
        context_docs = self.retrieve_context(query)

        if not context_docs:
            return {
                "answer": "Я не знаю. В моей базе знаний нет информации по этому вопросу.",
                "sources": [],
                "reasoning": None
            }

        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(query, context_docs)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False
                }
            )

            full_response = response.json()["message"]["content"]

            reasoning = None
            answer = full_response

            if "Рассуждение:" in full_response:
                parts = full_response.split("Ответ:")
                if len(parts) == 2:
                    reasoning = parts[0].replace("Рассуждение:", "").strip()
                    answer = parts[1].strip()

            sources = [
                {
                    "source": doc.metadata.get('source', 'unknown'),
                    "text": doc.page_content[:150]
                }
                for doc in context_docs
            ]

            return {
                "answer": answer,
                "reasoning": reasoning,
                "sources": sources
            }

        except Exception as e:
            return {
                "answer": f"Ошибка: {str(e)}",
                "sources": [],
                "reasoning": None
            }
