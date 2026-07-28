from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_bringup = FindPackageShare('my_robot_bringup')
    pkg_description = FindPackageShare('my_robot_description')
    pkg_slam_toolbox = FindPackageShare('slam_toolbox')

    # Paths
    default_slam_params_path = PathJoinSubstitution(
        [pkg_bringup, 'config', 'mapper_params_online_async.yaml']
    )
    default_ekf_params_path = PathJoinSubstitution(
        [pkg_bringup, 'config', 'ekf.yaml']
    )
    default_rviz_config_path = PathJoinSubstitution(
        [pkg_description, 'rviz', 'urdf_config.slam.rviz']
    )
    sim_launch_path = PathJoinSubstitution(
        [pkg_bringup, 'launch', 'sim.launch.py']
    )

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    rviz_config = LaunchConfiguration('rviz_config')

    # Arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock',
    )
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=default_slam_params_path,
        description='Path to slam_toolbox params',
    )
    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config_path,
        description='Path to RViz config',
    )

    # 1. Sim Launch (Gazebo, RSP, Bridge, Controllers, RViz)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch_path),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rviz_config': rviz_config,
            'use_rviz': 'true',
        }.items(),
    )

    # 2. EKF Node (fuses wheel odom + IMU -> broadcasts odom -> base_footprint)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            default_ekf_params_path,
            {'use_sim_time': use_sim_time}
        ],
    )

    slam_toolbox_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_slam_toolbox, 'launch', 'online_async_launch.py'])
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'slam_params_file': params_file,
            }.items(),
        )


    delayed_nodes = TimerAction(
        period=5.0,
        actions=[ekf_node, slam_toolbox_launch]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_params_file,
        declare_rviz_config,
        sim_launch,
        delayed_nodes,
    ])

