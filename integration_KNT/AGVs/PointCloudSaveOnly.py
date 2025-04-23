import numpy as np
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
import mapper
import time
from datetime import datetime
import sys
import os
import ctypes
import socket
import cv2

# This part is inspired by KonstantinosAng. Thx a lot!
class Cloud:

    def __init__(self, file="", color=False, depth=True):
        """
        Initializes the point cloud
        file: The dir to the point cloud (either .txt, .ply or .pcd file)
        color: Flag for displaying the color pointcloud dynamically
        depth: Flag for displaying the depth pointcloud dynamically
        :return None
        """
        # Initialize Kinect object
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color|PyKinectV2.FrameSourceTypes_Depth|PyKinectV2.FrameSourceTypes_Body|PyKinectV2.FrameSourceTypes_BodyIndex)
        self._cloud = False  # Flag to break loop when creating a pointcloud
        self._depth = None  # Store last depth frame
        self._color_frame = None  # store the last color frame
        self._color_point_cloud = color  # Flag to show dynamic point cloud using the color frame
        self._depth_point_cloud = depth  # Flag to show dynamic point cloud using the depth frame
        self._cloud_file = file  # Store the file name
        self._dir_path = os.path.dirname(os.path.realpath(__file__))  # Store the absolute path of the file
        self._dynamic_point_cloud = None  # Store the calculated point cloud points

        # check for multiple input flags or no input flags when using dynamic point cloud only
        if self._cloud_file != "":
            # check if file is not a txt and is a pcd file
            if self._cloud_file[-4:] == '.pcd' or self._cloud_file[-4:] == '.ply':
                self.visualize_file()
            elif self._cloud_file[-4:] == '.txt':
                self.init()  # Initialize the GL GUI
            else:
                if '.' in self._cloud_file:
                    extension = '.' + self._cloud_file.split('.')[-1]
                    print('[CloudPoint] Not supported file extension ({})'.format(extension))
                    print('[CloudPoint] Only .txt, .pcd or .ply files are supported')
                else:
                    print('[CloudPoint] Input has no valid file extension')
                sys.exit()

    def save_rgb(self):
        print('HERE!')
        rgb_img = np.reshape(self._color_frame, [1080, 1920, 4])[:, :, 0:3]
        rgb_img = rgb_img[:, :, 0:3]
        rgb_img = cv2.flip(rgb_img, 1)
        filepath = os.path.join(self._dir_path, self._cloud_file)[:-3]+'png'
        cv2.imwrite(filepath, rgb_img)

    def create_points(self):
        """
        Check if the file exists and if not create the point cloud points and the file
        :return None
        """
        # Check if the file exists in the folder
        if True:#not os.path.exists(os.path.join(self._dir_path, self._cloud_file)):
            t = time.time()  # starting time
            while not self._cloud:
                # ----- Get Depth Frame
                if self._kinect.has_new_depth_frame():
                    # store depth frame
                    self._depth = self._kinect.get_last_depth_frame()
                # ----- Get Color Frame
                if self._kinect.has_new_color_frame():
                    # store color frame
                    self._color_frame = self._kinect.get_last_color_frame()
                # wait for kinect to grab at least one depth frame
                if self._kinect.has_new_depth_frame() and self._color_frame is not None and self._dt > 6:

                    # use mapper to get world points
                    if self._depth_point_cloud:
                        world_points = mapper.depth_2_world(self._kinect, self._kinect._depth_frame_data, _CameraSpacePoint)
                        world_points = ctypes.cast(world_points, ctypes.POINTER(ctypes.c_float))
                        world_points = np.ctypeslib.as_array(world_points, shape=(self._kinect.depth_frame_desc.Height * self._kinect.depth_frame_desc.Width, 3))
                        world_points *= 1000  # transform to mm
                        self._dynamic_point_cloud = np.ndarray(shape=(len(world_points), 3), dtype=np.float32)
                        # transform to mm
                        self._dynamic_point_cloud[:, 0] = world_points[:, 0]
                        self._dynamic_point_cloud[:, 1] = world_points[:, 2]
                        self._dynamic_point_cloud[:, 2] = world_points[:, 1]

                        if self._cloud_file[-4:] == '.txt':
                            # remove zero depths
                            self._dynamic_point_cloud = self._dynamic_point_cloud[self._dynamic_point_cloud[:, 1] != 0]
                            self._dynamic_point_cloud = self._dynamic_point_cloud[np.all(self._dynamic_point_cloud != float('-inf'), axis=1)]

                        if self._cloud_file[-4:] == '.ply' or self._cloud_file[-4:] == '.pcd':
                            # self.save_rgb()
                            # update color for .ply file only
                            self._color = np.zeros((len(self._dynamic_point_cloud), 3), dtype=np.float32)
                            # map color to depth frame
                            Xs, Ys = mapper.color_2_depth_space(self._kinect, _ColorSpacePoint, self._kinect._depth_frame_data, show=False)
                            color_img = self._color_frame.reshape((self._kinect.color_frame_desc.Height, self._kinect.color_frame_desc.Width, 4)).astype(np.uint8)
                            # make align rgb/d image
                            align_color_img = np.zeros((self._kinect.depth_frame_desc.Height, self._kinect.depth_frame_desc.Width, 4), dtype=np.uint8)
                            align_color_img[:, :] = color_img[Ys, Xs, :]
                            align_color_img = align_color_img.reshape((self._kinect.depth_frame_desc.Height * self._kinect.depth_frame_desc.Width, 4)).astype(np.uint8)
                            align_color_img = align_color_img[:, :3:]  # remove the fourth opacity channel
                            align_color_img = align_color_img[..., ::-1]  # transform from bgr to rgb
                            self._color[:, 0] = align_color_img[:, 0]
                            self._color[:, 1] = align_color_img[:, 1]
                            self._color[:, 2] = align_color_img[:, 2]

                    if self._color_point_cloud:
                        # use mapper to get world points from color sensor
                        world_points = mapper.color_2_world(self._kinect, self._kinect._depth_frame_data, _CameraSpacePoint)
                        world_points = ctypes.cast(world_points, ctypes.POINTER(ctypes.c_float))
                        world_points = np.ctypeslib.as_array(world_points, shape=(self._kinect.color_frame_desc.Height * self._kinect.color_frame_desc.Width, 3))
                        world_points *= 1000  # transform to mm
                        # transform the point cloud to np (424*512, 3) array
                        self._dynamic_point_cloud = np.ndarray(shape=(len(world_points), 3), dtype=np.float32)
                        self._dynamic_point_cloud[:, 0] = world_points[:, 0]
                        self._dynamic_point_cloud[:, 1] = world_points[:, 2]
                        self._dynamic_point_cloud[:, 2] = world_points[:, 1]

                        if self._cloud_file[-4:] == '.txt':
                            # remove zeros from array
                            self._dynamic_point_cloud = self._dynamic_point_cloud[self._dynamic_point_cloud[:, 1] != 0]
                            self._dynamic_point_cloud = self._dynamic_point_cloud[np.all(self._dynamic_point_cloud != float('-inf'), axis=1)]

                        if self._cloud_file[-4:] == '.ply' or self._cloud_file[-4:] == '.pcd':
                            # update color for .ply file only
                            self._color = np.zeros((len(self._dynamic_point_cloud), 3), dtype=np.float32)
                            # get color image
                            color_img = self._color_frame.reshape((self._kinect.color_frame_desc.Height, self._kinect.color_frame_desc.Width, 4)).astype(np.uint8)
                            color_img = color_img.reshape((self._kinect.color_frame_desc.Height * self._kinect.color_frame_desc.Width, 4))
                            color_img = color_img[:, :3:]  # remove the fourth opacity channel
                            color_img = color_img[..., ::-1]  # transform from bgr to rgb
                            # update color with rgb color
                            self._color[:, 0] = color_img[:, 0]
                            self._color[:, 1] = color_img[:, 1]
                            self._color[:, 2] = color_img[:, 2]

                    # write points for txt file
                    if self._cloud_file[-4:] == '.txt':
                        row =''.join(','.join(str(point).strip('[]') for point in xyz) + '\n' for xyz in self._dynamic_point_cloud)
                        with open(os.path.join(self._dir_path, self._cloud_file), 'a') as txt_file:
                            txt_file.write(row)

                    self._cloud = True  # break loop
                self._dt = time.time() - t  # running time

    def load_data(self):
        """
        Calculates the point cloud points only for one time for initialization purposes only
        :return None
        """
        # check if points are produced from pointcloud
        if self._dynamic_point_cloud is None:
            # Load data if file already existed
            with open(os.path.join(self._dir_path, self._cloud_file), 'r') as file:
                # from string to float
                data = [x for x in file.read().split('\n')]
                data = [x.split(',') for x in data]
            # transform to array [:, 3]
            points = np.ndarray(shape=(len(data), 3), dtype=np.float32)
            for i, x in enumerate(data):
                try:
                    points[i] = [float(x[0]), float(x[1]), float(x[2])]
                except Exception as e:
                    pass
            # save points
            # self._dynamic_point_cloud = points[points[:, 1] != 0]  # its taken care in create_points function
            self._dynamic_point_cloud = points
        # save color for points
        self._color = np.zeros((self._dynamic_point_cloud.shape[0], 4), dtype=np.float32)

    def init(self):
        """
        Initialize PyQTGraph and add the constructed points
        :return None
        """
        # check if the pointcloud is dynamically
        self.create_points()
        self.load_data()  # load points for the first time

    def visualize_file(self):
        """
        Handles the .pcd or .ply files visualization with Open3D
        :return None
        """
        # create and save file
        self.create_points()
        if self._cloud_file[-4:] == '.ply':
            self.export_to_ply()
        if self._cloud_file[-4:] == '.pcd':
            self.export_to_pcd()
        sys.exit()  # exit the application

    def export_to_ply(self):
        """
        Inspired by https://github.com/bponsler/kinectToPly
        Writes a kinect point cloud into a .ply file
        return None
        """
        # assert that the points have been created
        assert self._dynamic_point_cloud is not None, "Point Cloud has not been initialized"
        assert self._cloud_file != "", "Specify text filename"
        # stack data
        data = np.column_stack((self._dynamic_point_cloud, self._color))
        data = data[np.all(data != float('-inf'), axis=1)]  # remove -inf
        # header format of ply file
        header_lines = ["ply",
                        "format ascii 1.0",
                        "comment generated by: python",
                        "element vertex {}".format(int(len(data))),
                        "property float x",
                        "property float y",
                        "property float z",
                        "property uchar red",
                        "property uchar green",
                        "property uchar blue",
                        "end_header"]
        # convert to string
        data = '\n'.join('{} {} {} {} {} {}'.format('%.2f' % -x[0], '%.2f' % x[1], '%.2f' % x[2], int(x[3]), int(x[4]), int(x[5])) for x in data)
        header = '\n'.join(line for line in header_lines) + '\n'
        # write file
        file = open(os.path.join(self._dir_path, self._cloud_file), 'w')
        file.write(header)
        file.write(data)
        file.close()
        self.save_rgb() # save RGB image for archive

    def export_to_pcd(self):
        # assert that the points have been created
        assert self._dynamic_point_cloud is not None, "Point Cloud has not been initialized"
        assert self._cloud_file != "", "Specify text filename"
        # pack r/g/b to rgb
        rgb = np.asarray([[int(int(r_g_b[0]) << 16 | int(r_g_b[1]) << 8 | int(r_g_b[0]))] for r_g_b in self._color])
        # stack data
        data = np.column_stack((self._dynamic_point_cloud, rgb))
        data = data[np.all(data != float('-inf'), axis=1)]  # remove -inf
        # header format of pcd file
        header_lines = ["# .PCD v0.7 - Point Cloud Data file format",
                        "VERSION 0.7",
                        "FIELDS x y z rgb",
                        "SIZE 4 4 4 4",
                        "TYPE F F F U",
                        "COUNT 1 1 1 1",
                        "WIDTH {}".format(int(len(data))),
                        "HEIGHT 1",
                        "VIEWPOINT 0 0 0 1 0 0 0",
                        "POINTS {}".format(int(len(data))),
                        "DATA ascii"]
        # convert to string
        data = '\n'.join('{} {} {} {}'.format('%.2f' % x[0], '%.2f' % x[1], '%.2f' % x[2], int(x[3])) for x in data)
        header = '\n'.join(line for line in header_lines) + '\n'
        # write file
        file = open(os.path.join(self._dir_path, self._cloud_file), 'w')
        file.write(header)
        file.write(data)
        file.close()

HOST = '0.0.0.0'  # 监听所有网络接口
PORT = 12345  # 端口号，可自定义
server_mode = False

if __name__ == "__main__":
    if server_mode:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            print('server activated, waiting for client...')
            conn, addr = server_socket.accept()
            with conn:
                print(f'client connected: {addr}')
                while True:
                    data = conn.recv(1024).decode(encoding='utf-8')
                    if not data:
                        break
                    elif data.strip().lower() == 's':
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        pcl = Cloud(file=f'savetest_0423/{timestamp}.ply', depth=True)
                    elif data.strip().lower() == 'e':
                        print('exit!')
                        break
                    else: print('invalid order!')
            conn.close()
    else:
        time.sleep(5)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pcl = Cloud(file=f'savetest_0423/{timestamp}.ply', depth=True)
