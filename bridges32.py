import os
import cv2 as cv
import numpy as np
import math

# Paths
img_path = 'images/img_001.png'
output_path = 'output_images/'
if not os.path.exists(output_path):
    os.mkdir(output_path)

###### IMPORTANT PARAMETERS ######
canny_low = 134 # hysteresis parameter
canny_high = 1050 # hysteresis parameter
canny_thickness = 1
rot_angle = 19.2
mpp = 1.28 # meter/pixel relation
px, py = (200,400) # arbitrary point coordinates
##################################

# Reading stage
img = cv.imread(img_path)
img_copy = cv.imread(img_path)
img_copy_32 = cv.imread(img_path)

# Create some zeros matrix to fit input image and make it a square
empty_img = np.zeros((img.shape[0], img.shape[1]))
empty_img_32 = np.zeros((img.shape[0], img.shape[1]))

# Define max value for tril & triu operations
diag = math.sqrt(img.shape[0]**2+img.shape[1]**2)
max = np.intp(diag/2)-10

### TRIL & TRIU PARAMETERS ####
triu_k1 = -1094
tril_k1 = 17
triu_k2 = -8
tril_k2 = max
###############################

# Canny & contour features stage
canny = cv.Canny(img, canny_low, canny_high)

(contours_1,_) = cv.findContours(canny.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
canny_2 = cv.drawContours(empty_img, contours_1, -1, (255), canny_thickness)

(contours_1_32,_) = cv.findContours(canny.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
canny_32 = cv.drawContours(empty_img_32, contours_1_32, -1, (255), 32)

# Create bars and concatenate to make square
bar = np.zeros(((img.shape[1] - img.shape[0])//2, img.shape[1]))

square = np.concatenate((bar, canny_2, bar), axis=0)
square_32 = np.concatenate((bar, canny_32, bar), axis=0)

# Rotation function, it will only work with square image inputs
def Rotate(input_img, angle):

    height = input_img.shape[0]
    width = input_img.shape[1]

    cy = height//2
    cx = width//2

    rot_matrix = cv.getRotationMatrix2D((cy, cx), angle, 1.0)

    cos = np.abs(rot_matrix[0][0])
    sen = np.abs(rot_matrix[0][1])

    output_height = int((height*sen) + (width*cos))
    output_width = int((height*cos) + (width*sen))

    rot_matrix[0][2] += (output_width/2) - cx
    rot_matrix[1][2] += (output_height/2) - cy

    rotada = cv.warpAffine(input_img, rot_matrix, (output_width, output_height))

    return rotada

# Rotation, tril & triu stage
rot = Rotate(square, rot_angle)
rot_32 = Rotate(square_32, rot_angle)
ret, rot = cv.threshold(rot, 63,255, cv.THRESH_BINARY)
ret, rot_32 = cv.threshold(rot_32, 63,255, cv.THRESH_BINARY)

rot_triu = np.triu(rot, triu_k1)
rot_triu_32 = np.triu(rot_32, triu_k1)

rot_triu_flip = np.flip(rot_triu, axis = 0)
rot_triu_flip_32 = np.flip(rot_triu_32, axis = 0)

rot_triu_flip_triu = np.triu(rot_triu_flip, triu_k2)
rot_triu_flip_triu_32 = np.triu(rot_triu_flip_32, triu_k2+3)

rot_triu_flip_triu_tril = np.tril(rot_triu_flip_triu, tril_k1)
rot_triu_flip_triu_tril_32 = np.tril(rot_triu_flip_triu_32, tril_k1)

flip_back = np.flip(rot_triu_flip_triu_tril, axis = 0)
flip_back_32 = np.flip(rot_triu_flip_triu_tril_32, axis = 0)

rot_back = Rotate(flip_back, -rot_angle)
rot_back_32 = Rotate(flip_back_32, -rot_angle)
ret,rot_back = cv.threshold(rot_back, 63, 255, cv.THRESH_BINARY)
ret,rot_back_32 = cv.threshold(rot_back_32, 63, 255, cv.THRESH_BINARY)

# Extract some values to recompose original shape of the segmented image
y0 = (rot_back.shape[0] - img.shape[0])//2
y1 = (rot_back.shape[0] - img.shape[0])//2 + img.shape[0]
x0 = (rot_back.shape[1] - img.shape[1])//2
x1 = (rot_back.shape[1] - img.shape[1])//2 + img.shape[1]

segmented = rot_back[y0:y1, x0:x1]
segmented_32 = rot_back_32[y0:y1, x0:x1]
segmented = segmented.astype(np.uint8)
segmented_32 = segmented_32.astype(np.uint8)

# Find & draw contours
(contours_2,_) = cv.findContours(segmented.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
(contours_2_32,_) = cv.findContours(segmented_32.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cv.drawContours(img_copy, contours_2, -1, (0, 0, 255), 2)
cv.drawContours(img_copy_32, contours_2_32, -1, (0, 0, 255), 2)

# Prepare for HBB & OBB extraction stages
blur = cv.GaussianBlur(segmented, (5,5), 0)
blur_32 = cv.GaussianBlur(segmented_32, (5,5), 0)
thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1] # umbral
thresh_32 = cv.threshold(blur_32, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1] # Thresh para minAreaRect
contours_3 = cv.findContours(thresh, cv.RETR_EXTERNAL, 2)
contours_3_32 = cv.findContours(thresh_32, cv.RETR_EXTERNAL, 2)

### HBB Extractions ###
x,y,w,h = cv.boundingRect(segmented)
cv.rectangle(img_copy, (x, y), (x + w, y + h), (0,255,0), 2)
x_32,y_32,w_32,h_32 = cv.boundingRect(segmented_32)
cv.rectangle(img_copy_32, (x_32, y_32), (x_32 + w_32, y_32 + h_32), (0,255,0), 2)

### OBB Extractions ###
cnt = contours_3[0]
cnt_32 = contours_3_32[0]
rect = cv.minAreaRect(cnt[0])
rect_32 = cv.minAreaRect(cnt_32[0])
box = cv.boxPoints(rect)
box = np.intp(box)
box_32 = cv.boxPoints(rect_32)
box_32 = np.intp(box_32)

# Measurements
length_pixels = math.sqrt(w**2 + h**2)
length_pixels_32 = math.sqrt(w_32**2 + h_32**2)
length_meters = float(length_pixels * mpp)
length_meters_32 = float(length_pixels_32 * mpp)

width_pixels = math.sqrt((box[1][0] - box[2][0])**2 + (box[1][1] - box[2][1])**2)
width_pixels_32 = math.sqrt((box_32[1][0] - box_32[2][0])**2 + (box_32[1][1] - box_32[2][1])**2)
width_meters = width_pixels * mpp
width_meters_32 = width_pixels_32 * mpp

area_pixels = length_pixels * width_pixels
area_pixels_32 = length_pixels_32 * width_pixels_32
area_meters = length_meters * width_meters
area_meters_32 = length_meters_32 * width_meters_32

M = cv.moments(cnt[0])
cx = int(M['m10'] / M['m00'])
cy = int(M['m01'] / M['m00'])

M_32 = cv.moments(cnt_32[0])
cx_32 = int(M['m10'] / M['m00'])
cy_32 = int(M['m01'] / M['m00'])

distance_pixels = math.sqrt((px - cx)**2 + (py - cy)**2)
distance_pixels_32 = math.sqrt((px - cx_32)**2 + (py - cy_32)**2)
distance_meters = distance_pixels * mpp
distance_meters_32 = distance_pixels_32 * mpp

# Text labels
length_label = f'The length of the bridge is {length_meters:.2f} meters.'
length_label_32 = f'The length of the bridge is {length_meters_32:.2f} meters.'
width_label = f'The width of the bridge is {width_meters:.2f} meters.'
width_label_32 = f'The width of the bridge is {width_meters_32:.2f} meters.'
area_label = f'The approximate area of the bridge is {area_meters:.2f} square meters.'
area_label_32 = f'The approximate area of the bridge is {area_meters_32:.2f} square meters.'
distance_label = f'The distance between the coordinate point ({px},{py}) and the center of the bridge is {distance_meters:.2f} meters.'
distance_label_32 = f'The distance between the coordinate point ({px},{py}) and the center of the bridge is {distance_meters_32:.2f} meters.'

# Add text labels to images
cv.putText(img_copy, length_label, (x+10, y+30), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy_32, length_label_32, (x_32+10, y_32+30), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy, width_label, (x+10, y+70), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy_32, width_label_32, (x_32+10, y_32+70), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy, area_label, (x+10, y+110), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy_32, area_label_32, (x_32+10, y_32+110), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy, distance_label, (x+10, y+150), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
cv.putText(img_copy_32, distance_label_32, (x_32+10, y_32+150), cv.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)

# Draw arbitrary point & path to center of the bridge
cv.circle(img_copy, (px, py), 12, (255, 0, 0), 2)
cv.circle(img_copy_32, (px, py), 12, (255, 0, 0), 2)
cv.line(img_copy, (px, py), (cx, cy), (255, 0, 0), 2)
cv.line(img_copy_32, (px, py), (cx, cy), (255, 0, 0), 2)

# Print measurements to console
print(f'The length of the bridge is {length_pixels_32} pixels equal to {length_meters_32} meters.')
print(f'The width of the bridge is {width_pixels_32} pixels equal to {width_meters_32} meters.')
print(f'The approximate area of the bridge is {area_pixels_32} square pixels equal to {area_meters_32} square meters.')
print(f'The distance between the coordinate point ({px}, {py}) and the center of the bridge is {distance_pixels_32} pixels equal to {distance_meters_32} meters.')

#cv.imshow('Imagen Original', img)
#cv.imshow('Contornos Canny', canny)
#cv.imshow('Imagen segmentada', segmentada)
#cv.imshow('Imagen encerrada', img_copy_3)
#cv.imshow('Imagen procesada', img_copy)
cv.imshow('Imagen refinada', img_copy_32)

cv.waitKey(0)
cv.destroyAllWindows()