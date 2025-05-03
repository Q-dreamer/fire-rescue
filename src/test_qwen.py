import os
from openai import OpenAI


class Model:
    def __init__(self):
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def chat(self, message, model="qwen-plus"):
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ],
            )
            return completion.model_dump_json()
        except Exception as e:
            print(f"Error in chat: {e}")
            raise e

model = Model()
response = model.chat("Hello, how are you?")
print(response)