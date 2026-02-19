#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import time
import os

import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class AIDeckPublisher(Node):

    def __init__(self):
        super().__init__('aideck_stream_publisher')

        # Parameters
        self.declare_parameter('ip', '192.168.4.1')
        self.declare_parameter('port', 5000)
        self.declare_parameter('save_flag', False)
        self.declare_parameter('show_flag', False)

        self.deck_ip = self.get_parameter('ip').value
        self.deck_port = self.get_parameter('port').value
        self.save_flag = self.get_parameter('save_flag').value
        self.show_flag = self.get_parameter('show_flag').value

        # Precomputed color correction factors
        self.factors = np.array([1.86, 1.26, 1.45], dtype=np.float32)

        # ROS publisher
        self.publisher_ = self.create_publisher(Image, 'aideck/image', 10)
        self.br = CvBridge()

        # Performance tracking
        self.start_time = time.time()
        self.frame_count = 0

        # Socket setup
        self.get_logger().info(f"Connecting to {self.deck_ip}:{self.deck_port}")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.deck_ip, self.deck_port))
        self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.get_logger().info("Socket connected")

        # Start streaming loop
        self.create_timer(0.0, self.stream_loop)  # Run as fast as possible

    # ===============================
    # Efficient socket reader
    # ===============================
    def rx_bytes(self, size):
        buffer = bytearray(size)
        view = memoryview(buffer)
        received = 0
        while received < size:
            n = self.client_socket.recv_into(view[received:])
            if n == 0:
                raise RuntimeError("Socket connection lost")
            received += n
        return buffer

    # ===============================
    # Fast color correction
    # ===============================
    def color_correct(self, img):
        img = img.astype(np.float32)
        img *= self.factors
        np.clip(img, 0, 255, out=img)
        return img.astype(np.uint8)

    # ===============================
    # Image Receiver
    # ===============================
    def get_image(self):

        packet_info = self.rx_bytes(4)
        length, routing, function = struct.unpack('<HBB', packet_info)

        img_header = self.rx_bytes(length - 2)
        magic, width, height, depth, fmt, size = struct.unpack('<BHHBBI', img_header)

        if magic != 0xBC:
            return None, None

        img_stream = bytearray(size)
        view = memoryview(img_stream)
        received = 0

        while received < size:
            packet_info = self.rx_bytes(4)
            length, dst, src = struct.unpack('<HBB', packet_info)
            chunk = self.rx_bytes(length - 2)
            view[received:received+len(chunk)] = chunk
            received += len(chunk)

        if fmt == 0:
            bayer = np.frombuffer(img_stream, dtype=np.uint8)
            bayer = bayer.reshape((244, 324))
            color = cv2.cvtColor(bayer, cv2.COLOR_BayerBG2BGR)
            return fmt, color
        else:
            nparr = np.frombuffer(img_stream, np.uint8)
            decoded = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            return fmt, decoded

    # ===============================
    # Streaming Loop
    # ===============================
    def stream_loop(self):

        fmt, img = self.get_image()

        if img is None:
            return

        if fmt == 0:
            img = self.color_correct(img)

        # Publish
        msg = self.br.cv2_to_imgmsg(img, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher_.publish(msg)

        # Optional display
        if self.show_flag:
            cv2.imshow("AIDeck", img)
            cv2.waitKey(1)

        # FPS calculation
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed
            self.get_logger().info(f"FPS: {fps:.2f}")


def main(args=None):
    rclpy.init(args=args)
    node = AIDeckPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
