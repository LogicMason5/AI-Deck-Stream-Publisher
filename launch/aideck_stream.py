from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Launch Configurations
    ip = LaunchConfiguration('ip')
    port = LaunchConfiguration('port')
    save_flag = LaunchConfiguration('save_flag')
    show_flag = LaunchConfiguration('show_flag')

    return LaunchDescription([

        # -------- Launch Arguments --------
        DeclareLaunchArgument(
            'ip',
            default_value='192.168.43.95',
            description='IP address of the AI deck device'
        ),

        DeclareLaunchArgument(
            'port',
            default_value='5000',
            description='Port number for streaming'
        ),

        DeclareLaunchArgument(
            'save_flag',
            default_value='false',
            description='Enable saving the stream to file'
        ),

        DeclareLaunchArgument(
            'show_flag',
            default_value='false',
            description='Enable live visualization window'
        ),

        # -------- Node --------
        Node(
            package='aideck_stream_publisher',
            executable='viewer',
            name='aideck_pub',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'ip': ip,
                'port': port,
                'save_flag': save_flag,
                'show_flag': show_flag,
            }]
        )
    ])
