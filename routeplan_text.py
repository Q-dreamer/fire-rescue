import base64
import re
from openai import OpenAI

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 图像编码
# base64_data = encode_image_to_base64("Figure_1.png")
# base64_data = encode_image_to_base64("Room_layout.png")
# base64_data = encode_image_to_base64("3D.png")
base64_data = encode_image_to_base64("new.png")
image_url = f"data:image/png;base64,{base64_data}"

client = OpenAI(
    api_key="sk-359bede07194494fb3f7e2c96069b89c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# System Prompt：火灾救援路径规划
system_prompt = """
你是一个火灾救援情境下的路径规划助手，需要根据用户提供的平面地图，救援人员，返回从起点到终点的行走路线。

**输出规则：**
1. 先识别地图中的关键地标（如无人机起点、Person终点、障碍物、物品名称等）。
2. 路径描述必须严格按以下格式：
   "从[起点名称]先走到[终点名称]"，例如："从大门走到喷泉，再从喷泉走到人"。
3. 红色区域是火源，必须绕行，不可碰；Person蓝色区域是待救援人员，即终点。
4. 如果无法识别路径，回答："未识别到起点和终点"。
"""

completion = client.chat.completions.create(
    model="qwen-vl-plus",
    messages=[
        {"role": "system", "content": system_prompt},  # 系统指令约束输出
        {"role": "user", "content": [
            {"type": "text", "text": "请规划图中从学习室到卧室的路径，严格按指定格式回答。"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]
)

# 提取模型回复
response = completion.choices[0].message.content
print("原始输出:", response)

# 后处理：用正则校验格式（可选）
pattern = r"从(.+)走到(.+)"
match = re.search(pattern, response)
if match:
    start, end = match.groups()
    print(f"校验通过 -> 起点: {start}, 终点: {end}")
else:
    print("格式不符合要求，请检查模型输出！")