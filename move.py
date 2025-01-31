#!/usr/bin/python
from core_tool import *
import rospy
import tf
from geometry_msgs.msg import PoseStamped
from omni_msgs.msg import OmniState
import time
import math
import numpy as np

def Help():

  return '''Position contorl script by haptics.
  Usage: haptics.position'''

def Run(ct, *args):
      
  x = ct.robot.FK()

  def cont(vel, i, rate):
    if abs(vel) < 1.0:
      pass
    else:
      x[i] += vel*rate

  def move(msg):
    rate = 1e-4*1.5
    rospy.loginfo(msg.velocity)
    cont(msg.velocity.x, 1, -rate)
    cont(msg.velocity.y, 0, rate)
    cont(msg.velocity.z, 2, rate)
    
    haps = [
      msg.pose.orientation.x,
      msg.pose.orientation.y,
      msg.pose.orientation.z,
      msg.pose.orientation.w  
    ]
    
    rotationX90 = tf.transformations.quaternion_about_axis(-math.pi/2, [1,0,0])
    rotationX90 = rotationX90.tolist()
    rotationY90 = tf.transformations.quaternion_about_axis(math.pi/2, [0,1,0])
    rotationY90 = rotationY90.tolist()
    rotationZ90 = tf.transformations.quaternion_about_axis(math.pi/2, [0,0,1])
    rotationZ90 = rotationZ90.tolist()

    rotation = tf.transformations.quaternion_multiply(rotationY90, haps)
    rotation = tf.transformations.quaternion_multiply(rotationX90, rotation)
    rotation = tf.transformations.quaternion_multiply(rotationZ90, rotation)
    rotation = tf.transformations.quaternion_multiply(rotationZ90, rotation)

    new = rotation
    new[1] = -new[1]
    new[2] = -new[2]

    for i, component in enumerate(new):
      x[i+3] = component
    ct.robot.MoveToX(x, 0.1)

  sub = rospy.Subscriber('/phantom/state', OmniState, move)
  rospy.spin()
  # r = rospy.Rate(0.5)
  # while not rospy.is_shutdown():
  #   r.sleep()