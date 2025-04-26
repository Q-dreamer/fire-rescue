import base64
import re
from openai import OpenAI
import queue
import speech_recognition as sr
from threading import Thread
import vosk # 语音输入（离线包）

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

system_prompt = """
你是一个火灾救援路径规划专家，需要根据平面地图生成详细的分步导航指令，你的目标是救援人员。
请严格遵循以下格式：

【路径规划步骤】
1. 从[起点名称]向[方向]移动至[节点1名称]（距离约X米）
   - 关键地标：[左侧/右侧]可见[地标名称]
   - 警告：[需要避开的危险区域]

2. 在[节点1名称][左转/右转/直行]至[节点2名称]
   - 方向指示：[具体转向说明]
   - 安全提示：[注意事项]

...（后续步骤）

【最终到达】[Person]并等待救援

输出规则：
1. 必须使用数字编号的步骤列表
2. 每个步骤必须包含：
   - 起点和终点名称（用[]标注） 
   - 明确方向指示
   - 关键地标参考
   - 危险区域提醒
3. 使用自然的方向描述（如"在第三个路口左转"）
"""

# 系统提示词 - 强化分步输出要求
# system_prompt = """
# 你是一个专业的火灾救援路径规划助手，需要根据提供的平面地图，给出从起点到终点的详细分步路线。
#
# 【输出要求】
# 1. 必须按照以下严格格式分步描述路径：
#
# 2. 必须包含以下关键信息：
# - 每个步骤的起点和终点
# - 方向指示（如"向左转"）
# - 危险区域提醒（如"绕过红色火源区"）
# - 关键地标提示（如"经过安全出口"）
#
# 3. 如果图中没有明确路径，回答："无法规划安全路径，建议重新选择路线"。
# """

# 初始化 Vosk 识别器
model = vosk.Model("vosk-model-cn-0.22")
recognizer = vosk.KaldiRecognizer(model, 16000)

# 语音输入线程
def voice_input_thread(q):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("麦克风已就绪，可以开始语音输入...")
        while True:
            print("请说话...")
            audio = r.listen(source, phrase_time_limit=6)  # 限制录音时长
            try:
                # 将音频数据转换为字节流
                data = audio.get_raw_data()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = result.strip('"')
                    q.put(text)
                    print("识别结果:", text)
            except Exception as e:
                print("识别失败:", e)

# 主程序
def main():
    q = queue.Queue()
    # 启动语音输入线程
    voice_thread = Thread(target=voice_input_thread, args=(q,), daemon=True)
    voice_thread.start()

    # 确保线程正常启动
    print("语音输入线程已启动，等待语音输入...")

    while True:
        try:
            user_text = q.get(timeout=10)  # 设置超时时间，避免无限期等待
            print("收到指令:", user_text)

            # 调用Qwen-VL模型处理
            completion = client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]}
                    # 示例对话强化输出格式
                    # {"role": "assistant", "content": """
                    # 【路径规划】
                    # 1. 从[正门]向[正北]移动
                    #    - 地标：左侧看到[]
                    #    - 注意：避开右侧[]
                    #
                    # 2. 在[安检通道]向[东偏北30度]行进
                    #
                    # 3. 从[扶梯口]向[东南]移动
                    #    - 地标：经过[]
                    #    - 准备：定位待救援人员
                    # """}
                ]
            )

            # 提取并解析模型回复
            response = completion.choices[0].message.content
            print("模型输出:", response)

        #     # 校验路径格式
        #     pattern = r"从(.+)走到(.+)"
        #     match = re.search(pattern, response)
        #     if match:
        #         start, end = match.groups()
        #         print(f"路径规划成功: 从【{start}】走到【{end}】")
        #     else:
        #         print("路径格式不符合要求！")
        # except queue.Empty:
        #     print("超时：未收到语音输入，继续等待...")
        # except Exception as e:
        #     print("主程序异常:", e)
        # 校验路径格式并提取详细节点信息
            pattern = r"从(.+?)走到(.+?)(?:，再从|$)"
            matches = re.findall(pattern, response)

            if matches:
                path = []
                for i in range(len(matches)):
                    if i == 0:
                        path.append(matches[i][0])  # 起点
                    path.append(matches[i][1])  # 中间节点或终点

                path_str = " → ".join(path)
                print(f"路径规划成功: {path_str}")
            else:
                print("路径格式不符合要求！")
        except queue.Empty:
            print("超时：未收到语音输入，继续等待...")
        except Exception as e:
            print("主程序异常:", e)

if __name__ == "__main__":
    main()