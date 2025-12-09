#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ams
from agvapi import Agv, findLineEdges
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from amsagv_msgs.msg import LineStamped
import math


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
    x, y, phi, gamma = 0.0, 0.0, 0.0, 0.0                     # Robot configuration
    fd = 0.0                                                  # Travelled distance of the front cart                                         
    V = 0.0                                                   # Velocity                                  
    anglOffset = 1325                                         # Branje senzorja kota - ravno
    wheelbase = 0.1207
    Lr = 0 
    Ll = 0
    startFlag = 0
    
    robot.readSensors()
    encLeft, encRight, encHeading = robot.getEncoders()
    
    encL = 0.1 / 11268                                        # encoder/meter (math.pow(2, 14))
    encR = 0.1 / 11456                                        # encoder/meter (math.pow(2, 14))
    Lr_old = encRight
    Ll_old = encLeft
    Lr = encRight * encR 
    Ll = encLeft * encL 
    
    

    rate = rospy.Rate(50)
    while not rospy.is_shutdown():
      t = rospy.Time.now()

      # Read sensors
      robot.readSensors()

      #
      # Odometry
      #

      # Encoders
      encLeft, encRight, encHeading = robot.getEncoders()

      #TODO Implement odometry here ...
      print('Encoders: left={}, right={}, heading={}'.format(encLeft, encRight, encHeading))
      
      gamma = -((encHeading - anglOffset) * 2 * math.pi) / 8192 # Kot / rotacija koles
      #gamma = ((encHeading - anglOffset) * 2 * math.pi) / math.pow(2,14) # Kot / rotacija koles
      
      # Stara razdalja za računanje delte
      Lr_old = Lr
      Ll_old = Ll
      
      # Pretvorba enkoder vrednosti v razdaljo
      Lr = encRight * encR 
      Ll = encLeft * encL 

      # Delta d posameznega kolesa
      Vl = Ll_old - Ll
      Vr = Lr - Lr_old  

      # Odometrija
      Vs = (Vl + Vr)/2
      print(Vl)
      print(Vr)
      fd += Vs
      V = Vs*math.cos(gamma)
      W = (Vs/wheelbase)*math.sin(gamma)
      phi = phi + W

      # X in Y koordinata agv-ja
      x = x + Vs * math.cos(phi)
      y = y + Vs * math.sin(phi) 
      
      # Init ob začetku programa (vse na 0)
      if startFlag == 0:
        x = 0
        y = 0
        Vs = 0
        W = 0
        phi = 0
        startFlag = 1                


      print('Odometry: speed={}, angle={}, distance={}'.format(V, math.degrees(gamma), fd))
      print('Coordinates: X={}, Y={}'.format(x, y, phi))

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

      rate.sleep()
  except KeyboardInterrupt:
    pass

