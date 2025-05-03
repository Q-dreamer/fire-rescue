import map, navigate

# 地图图片和对应的拓扑文件路径
PIC_PATH = "mappic.jpg"
TOPO_PATH = "maptopo.json"
NODE_START = 0


picmap = map.PictureMap(pic_path=PIC_PATH, topo_path=TOPO_PATH)
agent = navigate.Navigator(NODE_START)
# 主循环
while True:
    """
    1.获取当前节点的局部地图
    2.绘制带轨迹的语义地图
    3.传地图到agent
    4.走一步
    """

    local_map = picmap.get_local_map(agent.trajectory)
    semantic_map = picmap.annotate(agent.trajectory)
    agent.update_map(semantic_map)
    agent.take_a_step()
