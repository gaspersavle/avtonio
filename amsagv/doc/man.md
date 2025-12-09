Autonomous Mobile Systems (AMS) Automated Guided Vehicle (AGV)

# AGV

Use SSH to connect to the AGV:
```bash
ssh pi@192.168.000.000 #EDIT the IP address and user name!
```

You can use private/public keys to make the SSH authorization:
```bash
ssh-keygen
ssh-copy-id pi@192.168.000.000 #EDIT the IP address and user name!
```

# Installation

Edit the ROS setup file (`~/ros/setup.bash`):
```bash
#!/bin/bash
source "/opt/ros/noetic/setup.bash"
[ -f "${HOME}/ros/work/devel/setup.bash" ] && source "${HOME}/ros/work/devel/setup.bash"

export ROS_MASTER_URI="http://127.0.0.1:11311" #EDIT IP address of the master!
export ROS_IP="127.0.0.1" #EDIT IP address of the local machine!
export ROS_NAMESPACE="" #EDIT the namespace!

export ROS_WORKSPACE="${HOME}/ros/work"
export EDITOR="nano"

echo "ROS MASTER=${ROS_MASTER_URI} IP=${ROS_IP} NS=${ROS_NAMESPACE}"
```
Make sure that the file `~/.bashrc` contains the following lines:
```bash
alias ROS='source ~/ros/setup.bash'
ROS
```
Reload the BASH environment (e.g. `source ~/.bashrc` or close all open BASH sessions).

Create a ROS workspace if it does not exist yet:
```bash
mkdir -p ~/ros/work/src
cd ~/ros/work
catkin_init_workspace src
catkin_make
```
Reload the BASH environment again.

Copy `amsagv` package to the AGV (into the folder `~/ros/work/src`).
