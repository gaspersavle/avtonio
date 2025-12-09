#include "amsagv/LaserSim.h"
#include <amsagv/PlanarState.h>
#include <opencv2/core/mat.hpp>
#include <ros/time.h>

using namespace std;
using namespace cv;

class RayCache
{
public:
  inline explicit RayCache(double x, double y, double psi) :
    cs{cos(psi), sin(psi)},
    lray{-sin(psi), cos(psi), x * sin(psi) - y * cos(psi)}
  {
  }

public:
  Point2d cs;
  Point3d lray;
};

class LaserSim::Self
{
public:
  PlanarState state;
  vector<RayCache> rays;
};

LaserSim::LaserSim() : self{make_unique<Self>()}
{
  msg.header.frame_id = "world";
  msg.header.stamp = ros::Time(0);
  msg.range_min = 0.0;
  msg.range_max = 100.0;
  msg.angle_min = 0.0;
  msg.angle_max = 0.0;
  msg.angle_increment = 0.0;
  msg.scan_time = 0.0;
  msg.time_increment = 0.0;
}
LaserSim::~LaserSim() = default;
LaserSim::LaserSim(LaserSim &&) = default;
LaserSim &LaserSim::operator=(LaserSim &&) = default;

void LaserSim::setRays(int count, int fov)
{
  msg.ranges.resize(count);
  double beta = fov * M_PI / 180.0;
  msg.angle_increment = beta / (count - 1);
  msg.angle_min = -beta / 2.0;
  msg.angle_max = beta / 2.0;
  self->rays.reserve(count);
}

void LaserSim::setState(PlanarState const &stateLaser)
{
  self->state = stateLaser;
}

void LaserSim::reset()
{
  self->rays.clear();
  int k = 0;
  for (auto &range : msg.ranges) // For each ray
  {
    range = msg.range_max;
    
    // Ray
    double theta{(k++) * msg.angle_increment + msg.angle_min};
    self->rays.emplace_back(RayCache{self->state.p.x, self->state.p.y, self->state.phi + theta});
  }
}

void LaserSim::scan(vector<Point2d> const &shape)
{
  // Go through all the segments in the shape
  for (auto a = shape.cbegin(), b = shape.cbegin() + 1; a != shape.cend() && b != shape.cend(); ++a, ++b)
  {
    // Segment end points
    Point3d aa{*a};
    aa.z = 1.0;
    Point3d bb{*b};
    bb.z = 1.0;
    // Segment line
    Point3d lab = aa.cross(bb);
    // Normalization factor
    Point2d ba = *b - *a;
    ba /= ba.ddot(ba);
    // For each ray
    auto ray = self->rays.cbegin();
    for (auto & range : msg.ranges )
    {
      // Ray ang segment line intersection point
      Point3d pcross = ray->lray.cross(lab);
      Point2d pc{pcross.x / pcross.z, pcross.y / pcross.z};
      // Normalized position of the intersection point on the segment line
      double q = ba.ddot(pc - *a);
      // If the intersection point is on the segment
      if (q >= 0 && q <= 1)
      {
        // Range
        double r = (pc - self->state.p).ddot(ray->cs);
        if (r > 0 && r < range)
          range = r;
      }
      ++ray;
    }
  }
}

void LaserSim::scan(vector<vector<Point2d>> const &shapes)
{
  for (auto const &shape : shapes)
    scan(shape);
}
