#ifndef AMSAGV_PLANAR_STATE_H
#define AMSAGV_PLANAR_STATE_H

#include <opencv2/core/mat.hpp>
#include <geometry_msgs/TransformStamped.h>

class PlanarState
{
public:
  inline explicit PlanarState() = default;
  inline explicit PlanarState(geometry_msgs::TransformStamped const &msg)
  {
    p.x = msg.transform.translation.x;
    p.y = msg.transform.translation.y;
    phi = (msg.transform.rotation.w < 0 ? -2.0 : 2.0) * asin(msg.transform.rotation.z);
  }

  inline auto getA() const -> cv::Matx23f
  {
    return cv::Matx23f(cos(phi), -sin(phi), p.x, sin(phi), cos(phi), p.y);
  }

public:
  cv::Point2d p;
  double phi;
};

#endif //AMSAGV_PLANAR_STATE_H