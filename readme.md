# Differential Drive Robot Simulation & 2D SLAM

This project simulates a differential drive mobile robot in Gazebo Harmonic using ROS 2 Jazzy. It integrates hardware interfaces via `gz_ros2_control`, maps unknown indoor environments using `slam_toolbox`, and saves the resulting occupancy grid through Nav2's map server.

### Prerequisites & Setup

System: Ubuntu 24.04 running ROS 2 Jazzy and Gazebo Harmonic. 

- Clone the workspace
- Install dependencies

> Run all commands from the root directory `diff-drive-sim`.

```bash
rosdep install --from-paths src --ignore-src -r -y
```
- Build it with `colcon build --symlink-install`, and source `install/setup.bash`. If Gazebo fails to resolve visual or collision meshes referenced via `package://`, point `GZ_SIM_RESOURCE_PATH` to the install share directory:
```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$(pwd)/install/my_robot_description/share

```
In some slower systems gazebo may take too much time to start and cause issues. In that case you need to incread the wait time in timer action in `slam.launch.py`
```
TimerAction(
        period=10.0, # Adjust this based on how long Gazebo takes to load on your machine
        actions=[ekf_node, slam_toolbox_launch]
    )
```
and similar fix in `nav.launch.py`

### How to Run
1. **Launch the Simulation:**
Set `enable_odom_tf: true` to `false` in `my_robot_controllers.yaml`.
Bring up Gazebo, spawn the robot inside the maze world, configure bridges, and open RViz:
```bash
ros2 launch my_robot_bringup slam.launch.py
```
Give it some time to completely start.

Set your RViz fixed frame to `map`.
2. **Teleoperate the Robot and form the map:**
Control the bot using your keyboard. The controller requires stamped messages synced with simulation time:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/diff_drive_controller/cmd_vel -p stamped:=true -p use_sim_time:=true
```
Move slowly and cover the entire maze.

3. **Save the Occupancy Grid:**
Once the maze is fully covered, save the map files:
```bash
ros2 run nav2_map_server map_saver_cli -f src/my_robot_bringup/maps/maze_map
```
This is already available. So you can delete the existing map .pgm and .yaml.

4. **Run navigation**
Change `enable_odom_tf: false` to `true` in `my_robot_controllers.yaml`.
After the map is ready and saved run
```bash
ros2 launch my_robot_bringup navigation.launch.py
```
Give it some time to completely start.
Set a goal location on RViz and see the robot autonomously navigate.


### Hardware & Controller Notes

* In the robot's Xacro file, ensure the active plugin in the `<ros2_control>` block is `gz_ros2_control/GazeboSimSystem`. Switch to `mock_components/GenericSystem` only when debugging controllers isolated from physics.
* While `gz_ros2_control` spins up `controller_manager` automatically when Gazebo loads, `joint_state_broadcaster` and `diff_drive_controller` still need to be launched via spawner nodes.
* The drive controller listens for `geometry_msgs/msg/TwistStamped` on `/diff_drive_controller/cmd_vel`. Unstamped velocity commands will not drive the robot unless routed to the controller's unstamped topic.
* Initial 2d pose estimates in the map frame, better to add it in nav2 config yaml.
* Set /map to transient local.
* Remapped /odom to /diff_drive_controller/odom as a GroupAction on Nav2 Bringup launchfile.


### References

* [gz_ros2_control Documentation](https://github.com/ros-controls/gz_ros2_control/blob/rolling/doc/index.rst)
* [slam_toolbox GitHub Repository](https://github.com/SteveMacenski/slam_toolbox)
* Maze Environment: [github](https://github.com/w7v-1212/ROS2-Nav2-with-SLAM)


