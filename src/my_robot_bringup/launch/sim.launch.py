import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 1. Package Directories
    pkg_description = FindPackageShare('my_robot_description')
    pkg_bringup = FindPackageShare('my_robot_bringup')
    pkg_ros_gz_sim = FindPackageShare('ros_gz_sim')

    # 2. File Paths
    urdf_path = PathJoinSubstitution(
        [pkg_description, 'urdf', 'my_robot.urdf.xacro']
    )
    rviz_config_path = PathJoinSubstitution(
        [pkg_description, 'rviz', 'urdf_config.rviz']
    )
    bridge_config_path = PathJoinSubstitution(
        [pkg_bringup, 'config', 'ros_gz_bridge.yaml']
    )
    world_path = PathJoinSubstitution(
        [pkg_description, 'worlds', 'test_world.sdf']
    )
    controllers_config_path = PathJoinSubstitution(
        [pkg_bringup, 'config', 'my_robot_controllers.yaml']
    )

    rviz_config = LaunchConfiguration('rviz_config')
    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=rviz_config_path,
    )


    # 3. Environment Variable for Gazebo Resource Finding
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[PathJoinSubstitution([pkg_description, '..'])],
    )

    # 4. Process xacro command
    robot_description_content = Command(['xacro ', urdf_path])

    # 5. Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True,
        }],
        output='screen',
    )

    # 6. Gazebo Harmonic Simulation Launch
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])]
        ),
        launch_arguments={'gz_args': ['-r ', world_path]}.items(),
    )

    # 7. Spawn Robot into Gazebo Harmonic
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'my_diff_bot',
            '-z',
            '0.1',
        ],
        output='screen',
    )

    # 8. Bridge Node
    clock_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config_path, 'use_sim_time': True}],
        output='screen',
    )

    # 9. Controller Spawners
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--param-file',
            controllers_config_path,
        ],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--param-file', controllers_config_path],
    )

    # 10. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        declare_rviz_config,
        set_gz_resource_path,
        gazebo_sim,
        robot_state_publisher_node,
        spawn_entity_node,
        clock_bridge_node,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        rviz_node,
    ])