import base64
from openai import OpenAI

def encode_image_to_base64(image_path):
    """将图片编码为base64格式"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 图像编码
# base64_data = encode_image_to_base64("Figure_1.png")
# base64_data = encode_image_to_base64("Room_layout.png")
# base64_data = encode_image_to_base64("3D.png")
base64_data = encode_image_to_base64("new.png")
image_url = f"data:image/png;base64,{base64_data}"

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-359bede07194494fb3f7e2c96069b89c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 系统提示词 - 强化分步输出要求
system_prompt = """
你是一个专业的火灾救援路径规划助手，需要根据提供的平面地图，给出从起点到终点的详细分步路线。

【输出要求】
1. 必须按照以下严格格式分步描述路径：

2. 必须包含以下关键信息：
- 每个步骤的起点和终点
- 方向指示（如"向左转"）重点！！！！
- 危险区域提醒
- 关键地标提示

3. 如果图中没有明确路径，回答："无法规划安全路径，建议重新选择路线"。
"""

# 构建对话消息
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": [
        {"type": "text", "text": "请规划从当前位置到蓝色救援区域的最安全路径，要求分步详细说明。"},
        {"type": "image_url", "image_url": {"url": image_url}}
    ]},
    # 示例对话强化输出格式
    {"role": "assistant", "content": """
路径规划：
1. 从[]走到[]，直行约20米
2. 从[]左转走到[]，注意避开右侧红色火源
3. 从[]走到[]，上楼至2层
4. 从[]右转走到[]，"""}
]

# 调用大模型API
try:
    completion = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=messages,
        temperature=0.3,  # 降低随机性
        max_tokens=500  # 确保足够长的回复
    )

    # 处理模型响应
    response = completion.choices[0].message.content
    print("=" * 50)
    print("完整路径规划：")
    print(response)
    print("=" * 50)

    # 提取并打印格式化步骤
    print("\n格式化步骤：")
    steps = [step.strip() for step in response.split('\n')
             if step.strip().startswith(tuple(f"{i}." for i in range(1, 20)))]

    for i, step in enumerate(steps, 1):
        print(f"步骤{i}: {step.split('.', 1)[1].strip()}")

except Exception as e:
    print(f"API调用失败: {e}")