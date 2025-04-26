import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(10, 8))

# 设置房间背景
room = patches.Rectangle((0, 0), 10, 8, linewidth=2, edgecolor='black', facecolor='beige')
ax.add_patch(room)

# 绘制物品
items = [
    {"type": "potted plant", "pos": (2, 6), "size": 0.5},
    {"type": "potted plant", "pos": (8, 6), "size": 0.5},
    {"type": "pot", "pos": (2, 4), "size": 0.3},
    {"type": "potted plant", "pos": (8, 4), "size": 0.5},
    {"type": "sofa", "pos": (5, 3), "size": (2, 0.8)},
    {"type": "potted plant", "pos": (1, 2), "size": 0.5},
    {"type": "bed", "pos": (7, 1.5), "size": (2.5, 1.5)},
    {"type": "potted plant", "pos": (5, 1), "size": 0.5},
    # 新增元素
    {"type": "person", "pos": (9, 7), "size": 0.6, "color": "blue", "marker": "o"},
    {"type": "UVA", "pos": (1, 1), "size": 0.4, "color": "black", "marker": "."},
    {"type": "emergency_exit", "pos": (6.5, 7), "size": (1.5, 1)},
]

# 为每个物品创建图形和标签
for item in items:
    if item["type"] == "potted plant":
        ax.plot(item["pos"][0], item["pos"][1], 'g^', markersize=item["size"] * 80)
    elif item["type"] == "pot":
        ax.plot(item["pos"][0], item["pos"][1], 'ro', markersize=item["size"] * 80)
    elif item["type"] == "sofa":
        sofa = patches.Rectangle(
            (item["pos"][0] - item["size"][0] / 2, item["pos"][1] - item["size"][1] / 2),
            item["size"][0], item["size"][1],
            facecolor='brown', edgecolor='black'
        )
        ax.add_patch(sofa)
    elif item["type"] == "bed":
        bed = patches.Rectangle(
            (item["pos"][0] - item["size"][0] / 2, item["pos"][1] - item["size"][1] / 2),
            item["size"][0], item["size"][1],
            facecolor='lightblue', edgecolor='black'
        )
        ax.add_patch(bed)
    elif item["type"] == "emergency_exit":
        # 创建紧急出口矩形并添加到坐标轴
        emergency_exit = patches.Rectangle(
            (item["pos"][0] - item["size"][0] / 2, item["pos"][1] - item["size"][1] / 2),
            item["size"][0], item["size"][1],
            facecolor='green', edgecolor='black'
        )
        ax.add_patch(emergency_exit)  # 将紧急出口矩形添加到坐标轴中
    elif item["type"] in ["person", "UVA"]:
        ax.plot(item["pos"][0], item["pos"][1],
                marker=item.get("marker", "o"),
                color=item.get("color", "black"),
                markersize=item["size"] * 80)

    # 添加文字标签（无人机标签稍微偏移避免重叠）
    offset = 0.3 if item["type"] != "UVA" else 0.4
    ax.text(item["pos"][0], item["pos"][1] + offset, item["type"],
            ha='center', va='center', fontsize=10)

# 设置坐标轴和标题
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.set_aspect('equal')
ax.axis('off')
plt.title('Room Layout with Objects and Agents', pad=20)

plt.tight_layout()
plt.show()