### Prerequisites & Setup

System: Ubuntu 24.04 running ROS 2 Jazzy and Gazebo Harmonic. 

Diff drive robot packages for vizualization and simulate in Gazebo. 

```bash
rosdep install --from-paths src --ignore-src -r -y
```
Build it with `colcon build --symlink-install`, and source `install/setup.bash`. If Gazebo fails to resolve visual or 

collision meshes referenced via `package://`, point `GZ_SIM_RESOURCE_PATH` to the install share directory:
```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$(pwd)/install/my_robot_description/share

```


### How to Run
Launch simulation
```bash
ros2 launch my_robot_bringup sim.launch.py
```


Control the bot using your keyboard. The controller requires stamped messages synced with simulation time:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/diff_drive_controller/cmd_vel -p stamped:=true -p use_sim_time:=true
```


* While `gz_ros2_control` spins up `controller_manager` automatically when Gazebo loads, `joint_state_broadcaster` and `diff_drive_controller` still need to be launched via spawner nodes.
* The drive controller listens for `geometry_msgs/msg/TwistStamped` on `/diff_drive_controller/cmd_vel`. Unstamped velocity commands will not drive the robot unless routed to the controller's unstamped topic.
