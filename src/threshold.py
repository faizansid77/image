#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('image')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import matplotlib.pyplot as plt
import cv2
import os, glob
import numpy as np
import math

hue_thresh = 0
sat_thresh = 0
val_thresh = 185
canny_thresh_low = 5
canny_thresh_high = 150

kernel_size = 2
erode_iterations = 1

def hue(X):
  global hue_thresh
  hue_thresh = X
  #print("hue at %d"%X)

def kernel_change(X):
  global kernel_size
  kernel_size = max(1,X)

def iterations_change(X):
  global erode_iterations
  erode_iterations = X

def sat(X):
  global sat_thresh
  sat_thresh = X
  #print("sat at %d"%X)

def val(X):
  global val_thresh
  val_thresh = X
  #print("Val at %d"%X)

################################# utility functions

def select_rgb_white(image):
  # white color mask
  lower = np.uint8([120, 120, 120])
  upper = np.uint8([255, 255, 255])
  white_mask = cv2.inRange(image, lower, upper)
  return white_mask
def convert_hsv(image):
  return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
def convert_hls(image):
  return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
def select_hsv_white(image):
  converted = convert_hsv(image)
  # white color mask
  lower = np.uint8([  hue_thresh, sat_thresh,   val_thresh])
  upper = np.uint8([255, 255, 255])
  white_mask = cv2.inRange(converted, lower, upper)
  return white_mask
def convert_gray_scale(image):
  return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
def apply_smoothing(image,kernel_size=15):
  return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
def detect_edges(image):
  return cv2.Canny(image, canny_thresh_low, canny_thresh_low)
def filter_region(image, vertices):
  mask = np.zeros_like(image)
  if len(mask.shape)==2:
    cv2.fillPoly(mask, vertices, 255)
  else:
    cv2.fillPoly(mask, vertices, (255,)*mask.shape[2]) # in case, the input image has a channel dimension
    return cv2.bitwise_and(image, mask)
def select_region(image):
  rows, cols = image.shape[:2]
  bottom_left  = [cols*0.1, rows*0.95]
  top_left     = [cols*0.4, rows*0.6]
  bottom_right = [cols*0.9, rows*0.95]
  top_right    = [cols*0.6, rows*0.6]
  # the vertices are an array of polygons (i.e array of arrays) and the data type must be integer
  vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
  return filter_region(image, vertices)

def denoise(mask,kernel_size,iterations):
  element = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size,kernel_size))
  for i in range(erode_iterations):
    mask = cv2.erode(mask, element, iterations = 1)
    mask = cv2.dilate(mask, element, iterations = 1)
    return mask

##################################################################

def thresholdModel(cv_image):

  t1=select_hsv_white(cv_image)

  kernel = np.ones((kernel_size,kernel_size),np.uint8)
  t2 = cv2.erode(t1,kernel,iterations = erode_iterations)
  mask=t1
  mask=denoise(mask,kernel_size,erode_iterations)

  cv2.imshow("Image window", mask)

  cv2.createTrackbar('hue',"Image window",0,179,hue)
  cv2.createTrackbar('sat',"Image window",0,255,sat)
  cv2.createTrackbar('Val',"Image window",0,255,val)

  cv2.createTrackbar('erode_kernel_size',"Image window",0,15,kernel_change)
  cv2.createTrackbar('erode_iterations',"Image window",0,4,iterations_change)

  cv2.waitKey(3)
  return t2