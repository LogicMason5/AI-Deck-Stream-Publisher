from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Launch configurations
    ip_config = LaunchConfiguration('ip')
    port_config = LaunchConfiguration('port')
    save_flag_config = LaunchConfiguration('save_flag')
    show_flag_config = LaunchConfiguration('show_flag')

    return LaunchDescription([

        # Launch Arguments
        DeclareLaunchArgument(
            'ip',
            default_value='192.168.43.95',
            description='IP address of the AI Deck stream source'
        ),

        DeclareLaunchArgument(
            'port',
            default_value='5000',
            description='Port number used for streaming'
        ),

        DeclareLaunchArgument(
            'save_flag',
            default_value='False',
            description='Enable saving incoming frames'
        ),

        DeclareLaunchArgument(
            'show_flag',
            default_value='False',
            description='Enable real-time frame display'
        ),

        # Node Definition
        Node(
            package='aideck_stream_publisher',
            executable='viewer',
            name='aideck_pub',
            output='screen',
            emulate_tty=True,

            parameters=[
                {
                    'ip': ip_config,
                    'port': port_config,
                    'save_flag': save_flag_config,
                    'show_flag': show_flag_config
                }
            ]
        )
    ])
