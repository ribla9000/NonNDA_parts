from core.config import OPENAI_API_KEY
import openai


class AIChatBot:

    @staticmethod
    def tokenize_data(data: str, model="text-embedding-ada-002"):
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with client:
            result = client.embeddings.create(input=[data], model=model).data[0].embedding
            return result

    @staticmethod
    def create_message(bot_context: str, content: str, user_query: str):
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        prompt = [
                    {
                        "role": "system",
                        "content": bot_context,
                    },
                    {
                        "role": "user",
                        "content": f"Дай ответ на основе следующего текста:\n{content}",
                    },
                    {
                        "role": "user",
                        "content": f"Вот мой вопрос:\n{user_query}"
                    }
        ]
        with client:
            chat_completion = client.chat.completions.create(
                messages=prompt,
                model="gpt-3.5-turbo-1106",
                temperature=0
            )

        return chat_completion, prompt



