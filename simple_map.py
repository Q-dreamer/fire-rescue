import matplotlib.pyplot as plt
import numpy as np
import random
import base64
from io import BytesIO
from openai import OpenAI

plt.ion()


class RescueEnv:
    def __init__(self):
        self.num_points = 20
        self.points = np.random.rand(self.num_points, 2) * 10
        self.semantics = ["bedroom", "living room", "bathroom", "kitchen", "study room"] * 4
        self.fire_sources = random.sample(range(self.num_points), 3)
        self.trapped_person = random.choice([i for i in range(self.num_points) if i not in self.fire_sources])

        self.semantics_with_id = self.process_semantics()
        self.mark_special_points()

        self.start_point = random.choice([i for i in range(self.num_points)
                                          if i not in self.fire_sources and i != self.trapped_person])
        self.current_point = self.start_point
        self.trajectory = [self.points[self.current_point]]
        self.explored = set([self.current_point])
        self.known_map = {self.current_point: (self.points[self.current_point],
                                               self.semantics_with_id[self.current_point])}
        self.local_range = 2  # 初始探索范围扩大

    def process_semantics(self):
        semantics_with_id = []
        count = {}
        for sem in self.semantics:
            count[sem] = count.get(sem, 0) + 1
            semantics_with_id.append(f"{sem}{count[sem]}" if count[sem] > 1 else sem)
        return semantics_with_id

    def mark_special_points(self):
        for i in self.fire_sources:
            self.semantics_with_id[i] = "Fire Source"
        self.semantics_with_id[self.trapped_person] = "Trapped Person"


class RescueVisual:
    def __init__(self, env):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.env = env
        self.init_global_map()

    def init_global_map(self):
        self.ax1.set_title("Global Map (Hidden)")
        for i, (x, y) in enumerate(self.env.points):
            color = "red" if i in self.env.fire_sources else \
                "blue" if i == self.env.trapped_person else "green"
            self.ax1.scatter(x, y, c=color, s=100)
            self.ax1.text(x, y, f"{self.env.semantics_with_id[i]}\n({i})", fontsize=8, ha="right")
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(0, 10)

    def get_current_map_image(self):
        """生成带轨迹的探索地图Base64编码"""
        buf = BytesIO()
        self.fig.savefig(buf, format='png', bbox_inches='tight', dpi=80)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def update_map(self):
        self.ax2.clear()
        self.ax2.set_title(f"Exploration Trajectory (Step: {len(self.env.trajectory)})")
        self.ax2.set_xlim(0, 10)
        self.ax2.set_ylim(0, 10)

        # 绘制所有已知点
        for i in self.env.known_map:
            x, y = self.env.points[i]
            color = "red" if i in self.env.fire_sources else \
                "blue" if i == self.env.trapped_person else "green"
            self.ax2.scatter(x, y, c=color, s=100)
            self.ax2.text(x, y, f"{self.env.semantics_with_id[i]}\n({i})", fontsize=8, ha="right")

        # 突出显示当前点
        current_x, current_y = self.env.points[self.env.current_point]
        self.ax2.scatter(current_x, current_y, c='gold', s=200, marker='*')

        # 绘制轨迹
        self.ax2.plot(*zip(*self.env.trajectory), marker="o", color="orange", linestyle=':')

        plt.draw()
        plt.pause(0.8)


class RescueAI:
    def __init__(self, env, visual):
        self.env = env
        self.visual = visual
        self.client = OpenAI(
            api_key="sk-359bede07194494fb3f7e2c96069b89c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.last_direction = None  # 新增方向记忆

    def get_local_points(self):
        current_pos = self.env.points[self.env.current_point]
        return [
            (i, x, y, self.env.semantics_with_id[i], np.linalg.norm(current_pos - [x, y]))  # 修改这里
            for i, (x, y) in enumerate(self.env.points)
            if np.linalg.norm(current_pos - [x, y]) <= self.env.local_range
        ]

    def backup_strategy(self, local_points):
        """优化备用策略：朝向被困人员方向探索"""
        target_pos = self.env.points[self.env.trapped_person]
        current_pos = self.env.points[self.env.current_point]
        direction = target_pos - current_pos

        # 优先选择方向一致的未探索点
        candidates = []
        for p in local_points:
            if p[0] in self.env.explored or p[3] in ["Fire Source"]:
                continue

            vec = self.env.points[p[0]] - current_pos
            angle_diff = np.arccos(np.dot(direction, vec) / (np.linalg.norm(direction) * np.linalg.norm(vec) + 1e-6))

            candidates.append((p, angle_diff, p[4]))

        if candidates:
            sorted_candidates = sorted(candidates,
                                       key=lambda x: 0.6 * x[1] + 0.4 * x[2])
            return sorted_candidates[0][0][3]

        # 没有合适目标时随机选择
        return random.choice([p[3] for p in local_points if p[3] != "Fire Source"])

    def get_next_target(self):
        try:
            local_points = self.get_local_points()
            available_targets = [p[3] for p in local_points
                                 if p[3] not in ["Fire Source", "Trapped Person"]]

            # 直接检测是否发现被困人员
            for p in local_points:
                if p[3] == "Trapped Person":
                    return "Trapped Person"

            map_image = self.visual.get_current_map_image()

            prompt = f"""请分析救援地图：
- 当前所在：{self.env.semantics_with_id[self.env.current_point]}（编号{self.env.current_point}）
- 可选目标：{', '.join(available_targets)}
- 红色区域为火源，蓝色五角星为目标位置

请按以下策略选择：
1. 优先选择靠近地图中心区域的未探索点
2. 避免重复访问已探索区域
3. 选择与当前轨迹方向一致的目标"""

            response = self.client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": map_image}
                    ]
                }],
                max_tokens=50
            )

            target = response.choices[0].message.content.strip(" '\"")
            return target if target in available_targets else self.backup_strategy(local_points)

        except Exception as e:
            print(f"模型错误: {str(e)[:50]}...启用备用策略")
            return self.backup_strategy(local_points)


def main():
    env = RescueEnv()
    visual = RescueVisual(env)
    ai = RescueAI(env, visual)  # 传入visual实例

    max_steps = 20
    step = 0

    while env.current_point != env.trapped_person and step < max_steps:
        step += 1

        # 直接检测是否到达目标
        if env.current_point == env.trapped_person:
            break

        local_points = ai.get_local_points()
        print(f"\n== 第 {step} 步 ==")
        print(f"当前位置：{env.semantics_with_id[env.current_point]}({env.current_point})")

        target = ai.get_next_target()
        print(f"选择目标：{target}")

        # 执行移动（优化后的目标匹配逻辑）
        found = False
        for p in local_points:
            if p[3] == target:
                env.current_point = p[0]
                found = True
                break
        if not found:
            env.current_point = random.choice([p[0] for p in local_points if p[3] != "Fire Source"])

        # 安全检查
        if env.current_point in env.fire_sources:
            print("危险！进入火源区域！")
            break

        env.explored.add(env.current_point)
        env.trajectory.append(env.points[env.current_point])
        env.local_range += 0.8  # 降低范围扩展速度

        visual.update_map()

    plt.ioff()
    if env.current_point == env.trapped_person:
        print("\n★★★ 成功救援！ ★★★")
    else:
        print("\n!!! 救援失败 !!!")
    plt.show()


if __name__ == "__main__":
    main()