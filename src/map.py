import cv2
import json


class PictureMap:
    def __init__(self, pic_path, topo_path):
        try:
            self.pic = cv2.imread(pic_path)
            self.topo = json.loads(open(topo_path).read())
        except Exception as e:
            print(f"Error creating map: {e}")
            raise e

    def get_local_map(self, trajectory):
        return self.mask(trajectory)

    def get_coord(self, node_id):
        # Get the coordinates of the node from the topology
        if node_id in self.topo:
            return self.topo[node_id]
        else:
            raise ValueError(f"Node ID {node_id} not found in topology.")

    def annotate(self, node_trajectory):
        """
        在地图上标记轨迹
        """
        coord_trajectory = [self.get_coord(node) for node in node_trajectory]

        # Draw circles at each trajectory point
        for coord in coord_trajectory:
            cv2.circle(
                self.pic,
                (int(coord[0]), int(coord[1])),
                radius=10,
                color=(0, 0, 255),
                thickness=-1,
            )

        # Draw lines connecting the trajectory points
        for i in range(len(coord_trajectory) - 1):
            start_point = (int(coord_trajectory[i][0]), int(coord_trajectory[i][1]))
            end_point = (
                int(coord_trajectory[i + 1][0]),
                int(coord_trajectory[i + 1][1]),
            )
            cv2.line(map.pic, start_point, end_point, color=(255, 0, 0), thickness=2)

    def mask(self, node_trajectory):
        """
        根据轨迹生成遮罩后的地图
        """
        # Create a black mask of the same size as the map
        mask = cv2.cvtColor(self.pic, cv2.COLOR_BGR2GRAY)
        mask[:] = 0

        # Draw a white circle on the mask at the given trajectory coordinates
        coord_trajectory = [self.get_coord(node) for node in node_trajectory]
        for coord in coord_trajectory:
            cv2.circle(
                mask, (int(coord[0]), int(coord[1])), radius=50, color=255, thickness=-1
            )

        # Apply the mask to the original image
        masked_image = cv2.bitwise_and(self.pic, self.pic, mask=mask)

        return masked_image
