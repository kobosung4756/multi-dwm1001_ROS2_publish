from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='uwb_visualizer',
            executable='uwb_tag_publisher',
            name='uwb_tag_publisher_0',
            output='screen',
            parameters=[{'usb_port': '/dev/ttyACM0', 'topic_name': '/uwb_tag0'}]
        ),
        Node(
            package='uwb_visualizer',
            executable='uwb_tag_publisher',
            name='uwb_tag_publisher_1',
            output='screen',
            parameters=[{'usb_port': '/dev/ttyACM1', 'topic_name': '/uwb_tag1'}]
        ),
        Node(
            package='uwb_visualizer',
            executable='uwb_tag_publisher',
            name='uwb_tag_publisher_2',
            output='screen',
            parameters=[{'usb_port': '/dev/ttyACM2', 'topic_name': '/uwb_tag2'}]
        ),
        Node(
            package='uwb_visualizer',
            executable='uwb_tag_publisher',
            name='uwb_tag_publisher_3',
            output='screen',
            parameters=[{'usb_port': '/dev/ttyACM3', 'topic_name': '/uwb_tag3'}]
        ),
    ])
