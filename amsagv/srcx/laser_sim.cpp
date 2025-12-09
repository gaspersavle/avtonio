/* Laser scanner simulator

This is a simple simulator of a laser scanner.

# Usage

Define all the static transformations.
```
roslaunch amsagv global.launch
```
Add `static:=true` for static definition of the robots.

Start laser simulator.
```
rosrun amsagv laser_sim _laser_frame_id:="laser1" _robot_frame_ids:="base0 base2 base3 base4 base5" _fov:=180 _ray_count:=180
```

Open visualization in RViz.
```
roslaunch amsagv rviz.launch
```

![laser_sim_rviz_tf](img/laser_sim_rviz_tf.png "Visualization of laser scans in RViz.")

*/
#include <string>
#include <vector>
#include <iostream>

#include <ros/ros.h>
#include <tf2_ros/transform_listener.h>

#include <opencv2/core/core.hpp>
#include <opencv2/core/mat.hpp>

#include "amsagv/PlanarState.h"
#include "amsagv/LaserSim.h"

using namespace std;
using namespace cv;

auto main(int argc, char **argv) -> int
{
  ros::init(argc, argv, "laser_sim");
  ros::NodeHandle node;

  /*
   * Params
   */
  // Name of the world frame. All poses of the object are supposed to be available with respect to this world frame.
  string worldFrameId{"world"};
  ros::param::get("~world_frame_id", worldFrameId);
  // Name of the laser frame, in which the laser measurements are simulated.
  string laserFrameId{"laser"};
  ros::param::get("~laser_frame_id", laserFrameId);
  
  vector<string> robotFrameIds;
  {
    // A space-separated list of robot frame names.
    string str{""};
    ros::param::get("~robot_frame_ids", str);
    
    istringstream iss(str);
    robotFrameIds.assign(istream_iterator<string>{iss}, istream_iterator<string>());
  }
  // Number of laser rays.
  int rayCount{180};
  ros::param::get("~ray_count", rayCount);
   // Laser scanner field of view (FOV), in degrees.
  int fov{180};
  ros::param::get("~fov", fov);
   // Maximum laser ray range.
  float rangeMax{1.5};
  ros::param::get("~range_max", rangeMax);
  // Minimum laser ray range.
  float rangeMin{0.0};
  ros::param::get("~range_min", rangeMin);
  // Maximum frame time offset, in seconds.
  float frameOff{0.0};
  ros::param::get("~frame_off", frameOff);
  // Maximum frame age, in seconds.
  float frameAge{1.0};
  ros::param::get("~frame_age", frameAge);
  
  vector<Point2d> boundaryShape;
  {
    // A space-separated list of connected points that describe the shape of the boundary. Each point is represented as a pair of x and y value.
    string str{"0.0 0.0 2.2 0.0 2.2 1.8 0.0 1.8 0.0 0.0"};
    ros::param::get("~boundary_shape", str);
    
    istringstream iss(str);
    float x, y;
    while (iss >> x >> y)
      boundaryShape.emplace_back(Point2d(x, y));
  }
  
  vector<Point2d> robotShape;
  {
    // A space-separated list of connected points that describe the shape of the robot. Each point is represented as a pair of x and y value.
    string str{"-0.023 -0.048 0.170 -0.048 0.170 0.048 -0.023 0.048 -0.023 -0.048"};
    ros::param::get("~robot_shape", str);
    
    istringstream iss(str);
    float x, y;
    while (iss >> x >> y)
      robotShape.emplace_back(Point2d(x, y));
  }

  /*
   * TF listener
   */
  tf2_ros::Buffer tfBuffer;
  tf2_ros::TransformListener tfListener{tfBuffer};

  /*
   * Publishers
   */
  ros::Publisher pubLaser = node.advertise<sensor_msgs::LaserScan>("laser", 10); // Laser scan publisher.

  
  /*
   * Laser simulator
   */
  LaserSim laserSim;
  laserSim.msg.header.frame_id = laserFrameId;
  laserSim.msg.range_min = rangeMin;
  laserSim.msg.range_max = rangeMax;
  laserSim.setRays(rayCount, fov);

  /*
   * Main loop
   */
  ros::Rate rate(30);
  vector<PlanarState> states;
  states.reserve(robotFrameIds.size());
  while (node.ok())
  {
    /*
     * Get laser pose
     */
    geometry_msgs::TransformStamped tfLaser;
    try
    {
      auto now = ros::Time::now();
      tfLaser = tfBuffer.lookupTransform(worldFrameId, laserFrameId, ros::Time(0));
      if (tfLaser.header.stamp != ros::Time(0) && abs((now - tfLaser.header.stamp).toSec()) > frameAge)
      {
        throw tf2::TransformException("No new frame transformation.");
      }
    }
    catch (tf2::TransformException &ex)
    {
      ROS_WARN("Pose of the laser is not known yet. %s", ex.what());
      ros::Duration(1.0).sleep();
      continue;
    }
    PlanarState stateLaser{tfLaser};

    /*
     * Get poses of the robots
     */
    states.clear();
    for (auto const &robotFrameId : robotFrameIds)
    {
      try
      {
        auto tfRobot = tfBuffer.lookupTransform(worldFrameId, robotFrameId, tfLaser.header.stamp);
        states.emplace_back(PlanarState{tfRobot});
      }
      catch (tf2::TransformException &ex)
      {
        if (frameOff > 0.0)
        {
          try
          {
            auto tfRobot = tfBuffer.lookupTransform(worldFrameId, robotFrameId, ros::Time(0));
            if (abs((tfLaser.header.stamp - tfRobot.header.stamp).toSec()) < frameOff)
            {
              states.emplace_back(PlanarState{tfRobot});
            }
          }
          catch (tf2::TransformException &ex)
          {
          }
        }
      }
    }

    /*
     * Simulate laser
     */
    laserSim.setState(stateLaser);
    laserSim.reset();
    laserSim.scan(boundaryShape);
    vector<Point2d> shape;
    for ( auto const &state : states ) {
      transform(robotShape, shape, state.getA());
      laserSim.scan(shape);
    }
    laserSim.msg.header.stamp = tfLaser.header.stamp;

    // Publish laser
    pubLaser.publish(laserSim.msg);

    ros::spinOnce();
    rate.sleep();
  }

  return 0;
}
