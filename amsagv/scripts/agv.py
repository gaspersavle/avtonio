#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import ams
from agvapi import Agv, findLineEdges
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from amsagv_msgs.msg import LineStamped



with Agv() as robot:
  # Handle velocity commands
  def handleCmdVel(msg):
    global robot
    robot.setVel(msg.linear.x, msg.angular.z)



  try:
    rospy.init_node('agv')
    ns = rospy.get_namespace().lstrip('/')
    # Name of the odometry frame
    paramOdomFrameId = rospy.get_param('~odom_frame_id', '{}odom'.format(ns))
    # Name of the AGV frame
    paramAgvFrameId = rospy.get_param('~agv_frame_id', '{}agv'.format(ns))

    # Odometry publisher
    pubOdom = rospy.Publisher('odom', Odometry, queue_size=1)
    # Line sensor publisher
    pubLine = rospy.Publisher('line', LineStamped, queue_size=1)
    # Velocity commands subscriber.
    subCmdVel = rospy.Subscriber('cmd_vel', Twist, handleCmdVel)

    # Line-sensor message
    msgLine = LineStamped()

    # Odometry message
    msgOdom = Odometry()
    msgOdom.header.frame_id = paramOdomFrameId
    msgOdom.child_frame_id = paramAgvFrameId

    # Odometry initial state
    x, y, phi, gamma = 0.0, 0.0, 0.0, 0.0 # Robot configuration
    fd = 0.0 # Travelled distance of the front cart

    rate = rospy.Rate(50)

    encleft_prev = 0
    encright_prev = 0
    encheading_prev = 0

    robot.readSensors()
    encleft_prev, encright_prev, encHeading = robot.getEncoders()

    while not rospy.is_shutdown():
      t = rospy.Time.now()

      # Read sensors
      robot.readSensors()

      #
      # Odometry
      #

      # Encoders
      encLeft, encRight, encHeading = robot.getEncoders()
      #print(f"Left: {encLeft} | Right: {encRight} | Head: {encHeading}")

      #TODO Implement odometry here ...
      delta_l = encLeft - encleft_prev
      delta_r = encRight - encright_prev

      omega_l = -(delta_l*50)/2551
      omega_r = (delta_r*50)/2551

      gama = -encHeading/8192*2*np.pi + 1.224

      v_l = omega_l * (46.72/2000)
      v_r = omega_r * (46.72/2000)

      v_avg = (v_r + v_l)/2

      phi += (v_avg/0.1207)*np.sin(gama)/50
      x += v_avg/50 * np.cos(phi)*np.cos(gama) 
      y += v_avg/50 * np.sin(phi)*np.cos(gama)
      
      print(f"omega l: {omega_l}\nomega r: {omega_r}\n----------------------")
      print(f"Vl l: {v_l}\nv_r: {v_r}\nv_avg: {v_avg}\n----------------------")
      print(f"gama: {gama}\nphi: {phi}\n----------------------")
    #\ngama: {gama}\n-------------\nv r: {v_r}\nv l: {v_l}\n-------------\nv avg: {v_avg}\nphi: {phi}\nx: {x}\ny: {y}")

      # Odometry message
      msgOdom.header.stamp = t
      msgOdom.pose.pose = ams.poseToPoseMsg(x, y, phi)
      msgOdom.pose.pose.position.z = gamma
      # Publish odometry message
      pubOdom.publish(msgOdom)

      #
      # Line sensor
      #

      # Line-sensor values
      lineValues = robot.getLineValues()
      # Left and right line edge
      edgeLeft, edgeRight = findLineEdges(lineValues)

      # Line-sensor message
      msgLine.header.stamp = t
      msgLine.line.values = lineValues
      msgLine.line.left = edgeLeft if edgeLeft is not None else float('nan')
      msgLine.line.right = edgeRight if edgeRight is not None else float('nan')
      msgLine.line.heading = gamma
      msgLine.line.distance = fd
      # Publish line-sensor message
      pubLine.publish(msgLine)

      encleft_prev = encLeft
      encright_prev = encRight

      rate.sleep()
  except KeyboardInterrupt:
    pass
