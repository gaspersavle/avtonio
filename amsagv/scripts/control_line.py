#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ams
import rospy
from geometry_msgs.msg import Twist
from amsagv_msgs.msg import LineStamped, TagStamped
from math import pi, sin, cos, isnan
from world import MTAG



tag = None
smeri = []
cnt = 0
smer = 0
flag_virtual_tag = 4
trenutna_razdalja = 0 
# Handle line sensor
def handleLine(msg):
  global smer
  global cnt
  global flag_virtual_tag # samo flag za določanje računanja (1 - računaj, 0 - preverjaj pot, 2 - fizični tag)
  global trenutna_razdalja
  global smeri

  v, w = 0.0, 0.0

  v_max = 0.3
  Kp = 3 
  w_crte =0.98
  
  distance = msg.line.distance # Razdalja ki jo vrača odometrija
  #print("distance", distance)
  left = msg.line.left
  right = msg.line.right
  direction = left + right /2
  print(left, right, type(left), type(right))
  print(direction)
  v = 0
  w = 0

  if isnan(msg.line.left):
    v = 0
    w = 0
  else:
    center = msg.line.left-(w_crte/2)
    v = 0.1
    w = center * Kp


  # Velocity commands message
  msgCmdVel = Twist()
  msgCmdVel.linear.x = v
  msgCmdVel.angular.z = w
  # Publish velocity commands
  pubCmdVel.publish(msgCmdVel)



def handleTag(msg):
  global tag
  tag = MTAG.get(msg.tag.id, None)
  print('New tag: {} -> {}'.format(msg.tag.id, tag))



try:
  rospy.init_node('control_line')
  
  # Velocity commands publisher.
  pubCmdVel = rospy.Publisher('cmd_vel', Twist, queue_size=1)
  # Line sensor subscriber
  subLine = rospy.Subscriber('line', LineStamped, handleLine)
  # Tag subscriber
  subTag = rospy.Subscriber('tag', TagStamped, handleTag)

  rospy.spin()
except KeyboardInterrupt:
  pass
  # else:
  #   if isnan(msg.line.right):
  #     v = 0
  #     w = 0
  #   else:
  #     center = msg.line.right+(w_crte/2)
  #     v = 0.1
  #     w = center * Kp
