import openai
from core.config import OPENAI_API_KEY


class AssistantAPI:

    @staticmethod
    def assistant_chat(user_query: str):
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with client:
            # thread = client.beta.threads.create()
            # file_path = pathlib.Path("./articles.mdx")
            # with open(file_path, 'rb') as file:
            #     file_content = file.read()
            # file = client.files.create(
            #     file=file_content,
            #     purpose="assistants"
            # )
            message = client.beta.threads.messages.create(
                thread_id="",
                role="user",
                content=user_query,
                file_ids=[""]
            )

            run = client.beta.threads.runs.create(
                thread_id="",
                assistant_id="",
            )
            import time

            def wait_on_run(run, thread):
                while run.status == "queued" or run.status == "in_progress":
                    run = client.beta.threads.runs.retrieve(
                        thread_id="",
                        run_id=run.id,
                    )
                    time.sleep(0.5)
                return run

            run = wait_on_run(run, "",)
            messages = client.beta.threads.messages.list(thread_id="",)

        return messages
