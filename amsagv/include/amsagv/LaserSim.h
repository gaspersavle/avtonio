#ifndef AMSAGV_LASER_SIM_H
#define AMSAGV_LASER_SIM_H

#include <memory>
#include <vector>
#include <sensor_msgs/LaserScan.h>

namespace cv
{
template <typename> class Point_;
typedef Point_<double> Point2d;
}

class PlanarState;

class LaserSim
{
public:
  explicit LaserSim();
  ~LaserSim();
  LaserSim(LaserSim &&);
  LaserSim &operator=(LaserSim &&);

  void setRays(int count, int fov);  
  
  void setState(PlanarState const &stateLaser);

  void reset();
  void scan(std::vector<cv::Point2d> const &shape);
  void scan(std::vector<std::vector<cv::Point2d>> const &shapes);

public:
  sensor_msgs::LaserScan msg;
private:
  class Self;
  std::unique_ptr<Self> self;
};

#endif //AMSAGV_LASER_SIM_H
