#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 이 스크립트는 UWB 태그의 위치 정보를 읽어와 ROS2 토픽으로 publish하여 RViz에서 시각화할 수 있도록 합니다.

# -------------------------------
# 표준 라이브러리 임포트
# -------------------------------
from pathlib import Path         # 파일 경로를 다루기 위한 모듈
import sys                       # 시스템 관련 기능(경로 추가 등)에 사용
from typing import NoReturn      # 함수 리턴 타입 표기를 위한 모듈

# -------------------------------
# 서드파티 라이브러리 임포트
# -------------------------------
from serial import Serial        # 시리얼 통신을 위해 pyserial의 Serial 클래스를 사용

# -------------------------------
# ROS2 관련 라이브러리 임포트
# -------------------------------
import rclpy                     # ROS2 클라이언트 라이브러리 초기화 및 스핀 기능 제공
from rclpy.node import Node      # ROS2 노드 클래스 제공
from geometry_msgs.msg import PoseStamped  # RViz에서 위치 시각화에 사용할 메시지 타입

# -------------------------------
# UWB 태그 관련 라이브러리(pydwm1001) 임포트
# -------------------------------
# pydwm1001 라이브러리가 설치되지 않은 상태에서도 현재 부모 디렉터리에서 코드를 찾을 수 있도록 경로 추가
sys.path.append(str(Path(__file__).resolve().parents[2]))
import dwm1001                 # UWB 태그 관련 기능을 제공하는 라이브러리

# -------------------------------
# UWB 태그 정보를 읽어와 ROS2 토픽으로 publish하는 노드 클래스 정의
# -------------------------------
class UwbTagPublisher(Node):
    # 노드 초기화 함수
    def __init__(self):
        # 'uwb_tag_publisher'라는 이름의 ROS2 노드 생성 및 초기화
        # 부모 클래스(Node)의 __init__ 메소드를 호출하여 노드를 'uwb_tag_publisher'라는 이름으로 초기화합니다.
        super().__init__('uwb_tag_publisher')
        # 이제 UwbTagPublisher 클래스는 Node 클래스의 모든 기능(예: publisher 생성 등)을 사용할 수 있습니다.
        
        # 파라미터 선언 (기본값: "/dev/ttyACM0")
        self.declare_parameter('usb_port', '/dev/ttyACM0')
        usb_port = self.get_parameter('usb_port').value

        # topic_name 파라미터 선언 (기본값 "uwb_tag")
        self.declare_parameter('topic_name', 'uwb_tag')
        topic_name = self.get_parameter('topic_name').value
        self.get_logger().info(f"Using USB port: {usb_port}, Topic: {topic_name}")
        
        # geometry_msgs/PoseStamped 메시지를 publish할 퍼블리셔 생성
        # 'uwb_tag' 토픽으로 최대 10개의 메시지를 큐잉하여 전달
        self.publisher_ = self.create_publisher(PoseStamped, topic_name, 10)

        # 시리얼 포트 설정: "/dev/ttyACM0" 포트를 사용하며 보드레이트는 115200bps로 설정
        self.serial_handle = Serial(usb_port, baudrate=115_200)
        
        # pydwm1001 라이브러리의 ActiveTag 클래스를 이용해 UWB 태그 객체 생성
        self.tag = dwm1001.ActiveTag(self.serial_handle)
        
        # UWB 태그의 위치 정보 보고 시작 (내부적으로 주기적으로 데이터 업데이트)
        self.tag.start_position_reporting()
        
        # 타이머 생성: 0.1초(10Hz)마다 timer_callback() 함수 호출
        self.timer = self.create_timer(0.1, self.timer_callback)
    
    # 타이머 콜백 함수: 주기적으로 호출되어 UWB 태그의 위치 정보를 읽고 ROS2 메시지로 publish함
    def timer_callback(self):
        # PoseStamped 메시지 객체 생성 (RViz에서 태그 위치 시각화에 사용)
        msg = PoseStamped()
        
        # 메시지 헤더에 현재 시간을 기록 (시각화 시 시간 정보를 위해 필요)
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 메시지 헤더의 frame_id를 "map"으로 설정 (RViz에서 좌표계를 설정할 때 사용)
        msg.header.frame_id = "map"
        
        # UWB 태그의 위치 정보를 읽어옴. 여기서는 tag.position이 (x, y, z) 좌표 튜플이라고 가정합니다.
        pos = self.tag.position  # 예: (x, y, z)
        
        # 읽어온 좌표를 메시지의 position 필드에 할당
        msg.pose.position.x = float(pos.x_m)
        msg.pose.position.y = float(pos.y_m)
        msg.pose.position.z = float(pos.z_m)
        
        # orientation 값은 제공되지 않는 경우 기본 단위 쿼터니언으로 설정
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0
                
        # 구성한 메시지를 'uwb_tag' 토픽으로 publish (RViz에서 이 토픽을 구독하여 태그 위치를 확인할 수 있음)
        self.publisher_.publish(msg)
        
        # 디버깅용 로그 출력 (필요시 활성화)
        self.get_logger().debug(
            f"Published UWB tag position: x={msg.pose.position.x}, y={msg.pose.position.y}, z={msg.pose.position.z}"
        )

# -------------------------------
# 메인 함수: ROS2 초기화, 노드 생성 및 스핀 실행
# -------------------------------
def main() -> NoReturn:
    # ROS2 클라이언트 라이브러리 초기화 (명령행 인자 전달 가능)
    rclpy.init()
    
    # UWB 태그 정보를 publish하는 노드 생성
    node = UwbTagPublisher()
    
    # 노드를 스핀하여 타이머 콜백 등 이벤트를 지속적으로 처리 (Ctrl+C로 종료)
    rclpy.spin(node)
    
    # 노드 종료 및 리소스 정리
    node.destroy_node()
    rclpy.shutdown()

# -------------------------------
# 스크립트가 직접 실행될 때 main() 함수를 호출
# -------------------------------
if __name__ == "__main__":
    main()
