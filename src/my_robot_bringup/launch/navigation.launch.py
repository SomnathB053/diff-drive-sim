from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import SetRemap
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_bringup = FindPackageShare('my_robot_bringup')
    pkg_nav2_bringup = FindPackageShare('nav2_bringup')
    pkg_description = FindPackageShare('my_robot_description')

    default_map_path = PathJoinSubstitution(
        [pkg_bringup, 'maps', 'maze_map.yaml']
    )
    default_nav2_params_path = PathJoinSubstitution(
        [pkg_bringup, 'config', 'nav2_params.yaml']
    )
    default_rviz_config_path = PathJoinSubstitution(
            [pkg_description, 'rviz', 'urdf_config.nav2.rviz']
        )
    sim_launch_path = PathJoinSubstitution(
            [pkg_bringup, 'launch', 'sim.launch.py']
        )
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    rviz_config = LaunchConfiguration('rviz_config')

    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    declare_map = DeclareLaunchArgument('map', default_value=default_map_path)
    declare_params_file = DeclareLaunchArgument('params_file', default_value=default_nav2_params_path)
    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config_path,
        description='Path to RViz config',
    )
    sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim_launch_path),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'rviz_config': rviz_config,
                'use_rviz': 'true',
            }.items(),
        )
    nav2_bringup_launch = GroupAction(
        actions=[
            SetRemap(src='/odom', dst='/diff_drive_controller/odom'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([pkg_nav2_bringup, 'launch', 'bringup_launch.py'])
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'map': map_yaml_file,
                    'params_file': params_file,
                    'autostart': 'true',
                    'use_collision_monitor': 'False',
                    'use_docking': 'False',
                }.items(),
            )
        ]
    )
    delayed_nav2 = TimerAction(
            period=5.0,
            actions=[nav2_bringup_launch])
    
    return LaunchDescription([
        declare_use_sim_time,
        declare_map,
        declare_params_file,
        declare_rviz_config,
        sim_launch,
        delayed_nav2
    ])