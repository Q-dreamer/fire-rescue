from test_qwen import Model
class Navigator:
    def __init__(self, start):
        self.curr_node = start
        self.trajectory = [start]
        self.map = None
        self.model = Model()

    def update_map(self, new_map):
        self.map = new_map

    def generate_prompt(self):
        """
        TODO 生成提示词
        提示词要包含：
        1.角色定义
        2.当前任务
        3.输入地图格式的简要描述（如何理解地图）
        4.输出要求
        """

    def take_a_step():
        """
        TODO 走一步
        1.交给大模型
        2.更新curr_node, trajectory
        """
        pass