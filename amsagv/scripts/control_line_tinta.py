#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ams
import rospy
from geometry_msgs.msg import Twist
from amsagv_msgs.msg import LineStamped, TagStamped, ActionsStamped
from math import pi, sin, cos, isnan
from world import MTAG
import numpy as np

# Init spremenlivke
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
  #print(msg.line.left- msg.line.right)

  v, w = 0.0, 0.0

  v_max = 0.3
  Kp = 3 
  w_crte =0.98
  
  distance = msg.line.distance # Razdalja ki jo vrača odometrija
  #print("distance", distance)
  
  if smer: 
    if isnan(msg.line.left):
      v = 0
      w = 0
    else:
      center = msg.line.left-(w_crte/2)
      v = 0.1
      w = center * Kp
      #if w == 0:
      #  v = v_max
  else:
    if isnan(msg.line.right):
      v = 0
      w = 0
    else:
      center = msg.line.right+(w_crte/2)
      v = 0.1
      w = center * Kp
      #if abs(w) <= 5:
      #  v = v_max
      
      
  ###### Naša koda ######

  # Dokler je etapa v predvideni poti in da pot sploh obstaja
  if len(smeri) != 0 and cnt < len(smeri):

    # 1) Naslednji tag je virtualen: shrani trenutno razdaljo, izvede samo enkrat
    if flag_virtual_tag == 0:  
      print("Virtual tag setup!")
      etapa = smeri[cnt]
      if etapa[1] != 0:   # Preveri da res ni fizičen tag (fizični imajo razdaljo 0)
        flag_virtual_tag = 1
        trenutna_razdalja = distance
        smer = etapa[0]
        print("Smer:", smer)
        print("Cnt:", cnt)

    # 2) Naslednji tag je virtualen: preverjanje kdaj ga zadanemo
    if flag_virtual_tag == 1:
      distance_to = distance - trenutna_razdalja  # Računanje ali smo na virtualnem tagu ali ne
      print("Distance to tag: ", distance_to, ":", smeri[cnt][1])

      if distance_to >= smeri[cnt][1]: # ko dosežemo delto med hranjeno in prevoženo razdaljo v velikosti željene poti
        cnt += 1
        print("Virtual tag dosežen...")
        
        if cnt < len(smeri):
          if int(smeri[cnt][2]) >= 100:
            flag_virtual_tag = 0        # Ponovno izvedi računanje virtualnega taga
            print("Naslednji tag je virtualen")
          else:
            flag_virtual_tag = 2        # Blokiraj akcije virtualnih tagov
            print("Naslednji tag je fizičen")

    # 3) Naslednji tag je fizičen: samo čakamo da ga zaznamo (koda v funkciji taga)

  # Konec poti
  else: 
    if cnt >= len(smeri) and len(smeri) != 0:
      v = 0.0
      w = 0.0
      flag_virtual_tag = 3
      print("Konec!") 
    

  # Velocity commands message
  msgCmdVel = Twist()
  msgCmdVel.linear.x = v
  msgCmdVel.angular.z = w
  # Publish velocity commands
  pubCmdVel.publish(msgCmdVel)


###### Obdelava označene poti - izvede se samo enkrat ob novi poti ######
def handleActions(msg):
  global tag
  global smer
  global cnt
  global smeri # dodano
  global flag_virtual_tag
  #print(msg)
  pot = msg.actions

  cnt = 0     # ponastavi števec
  smeri = []  # izprazni list etap

  # smeri: list etap ki jih more agv opravit [smer, razdalja, id taga]
  #   + smer: 1 - levo, 0 - desno
  #   + razdalja: 0 - fizičen tag, n - virtualen tag
  #   + id taga: id trenutnega taga

  for p in pot:
    
    # Tag je fizičen
    if p.action.id < 100: 
      if p.action.name == "left":
        smeri.append([1,0,p.action.id])
      else:
        smeri.append([0,0,p.action.id])

    # Tag je virtualen     
    else: 
      if p.action.name == "left": 
        smeri.append([1,p.action.distance,p.action.id])
      else:
        smeri.append([0,p.action.distance,p.action.id])
        
  print("smeri:", smeri)

  # Nastavi flag_virtual_tag za prvi tag (glede na vrednost razdalje - 0 = fizični tag)
  if smeri[0][1] != 0:
    flag_virtual_tag = 0 # Virtual (računaj)
  else:
    flag_virtual_tag = 2 # Fizični (zaznavaj)
      
###### Zaznavanje tag_readerja ######
def handleTag(msg):
  global tag
  global smer
  global smeri
  global cnt
  global flag_virtual_tag
  
  tag = MTAG.get(msg.tag.id, None) # tag_id
  if tag == None: return # Če je tag None ne ga upoštevat

  print('New tag: {} -> {}'.format(msg.tag.id, tag))
  
  if len(smeri) != 0 and cnt < len(smeri): # blokiraj če ni poti ali je konec poti             
    cnt += 1 

    if cnt < len(smeri):
      etapa = smeri[cnt]      # podatki o trenutni etapi do naslednjega taga
      smer = etapa[0]         # nastavi smer (ni važna vrsta taga)
      print("Smer:", smer)

      # Preveri tag_id in glede na to postavi flag
      if int(etapa[2]) >= 100: # and cnt <= len(smeri)
        flag_virtual_tag = 0  # Sproži nastavljanje vrednosti za virtualen tag   
        print("Razdalja:", str(smeri[cnt][2]))
        print("Flag: flag_virtual_tag = 0")

      # Zaznavanje tegov če agv ne začne na začetku poti (cnt se uskladi s potjo in nadaljuje s te točke)
      # for index in range(len(smeri)):
      #   s = smeri[index]
      #   if tag == s[2]:       # preveri če je trenuten tag enak pričakovanemu
      #     if cnt <= index:
      #       cnt = index+1
      #       print("Popravljam pot!")
      #       print("Smer:", smer)
      #       print("Cnt:", cnt)
      #       print("Razdalja:", str(smeri[cnt][2]))
      #       break

try:
  rospy.init_node('control_line')
  
  # Velocity commands publisher.
  pubCmdVel = rospy.Publisher('cmd_vel', Twist, queue_size=1)
  # Line sensor subscriber
  subLine = rospy.Subscriber('line', LineStamped, handleLine)
  # Tag subscriber
  subTag = rospy.Subscriber('tag', TagStamped, handleTag)
  #actions sub
  rospy.Subscriber('path_actions', ActionsStamped, handleActions)

  rospy.spin()
except KeyboardInterrupt:
  pass


