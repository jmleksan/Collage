import cv2
import numpy as np
import os
import json

def import_image(file):
    return cv2.imread(file)

def average_color(image):
    pixal = np.array([0,0,0])
    for i in range(image_width(image)):
        for j in range(image_height(image)):
            pixal += image[i,j]
    pixal = pixal / (image_height(image) * image_width(image))
    return pixal

def image_width(image):
    return image.shape[0]

def image_height(image):
    return image.shape[1]

def crop_image(image,x1,x2,y1,y2):
    crop_image = image[x1:x2,y1:y2]
    return crop_image

def crop_source(image):
    w = image_width(image)
    h = image_height(image)
    if w > h:
        m = w/2
        crop_image = image[int(m - w/2):int(m + w/2),0:h]
    else:
        m = h/2
        crop_image = image[0:w,int(m - h/2):int(m + h/2)]
    return crop_image

def edit_source_files(path, directory,base_directory):
    os.chdir(path)
    if os.path.isdir(directory) == False:
        os.mkdir(directory)
    for files in os.listdir(path):
        if os.path.isfile(files) == False:
            os.chdir(path)
            image = cv2.imread(files)
            crop_image = crop_source(image)
            os.chdir(directory)
            cv2.imwrite(files,crop_image)
    os.chdir(base_directory)    
    return directory

def find_source_color(path,base_directory):
    if os.path.isfile('colors.json') == True:
        file = open('colors.json')
        colors = json.load(file)
    else:
        os.chdir(path)
        colors = {}
        for files in os.listdir(path):
            image = cv2.imread(files)
            color = average_color(image)
            colors[files] = {'red': color[0], 'green': color[1], 'blue': color[2]}
        os.chdir(base_directory)
        with open('colors.json', 'w') as file:
            json.dump(colors, file)
    return colors

def color_in(pixals,color,width,height,x1,y1):
    for i in range(width):

        if x1 + i >= image_width(pixals):
            continue

        for j in range(height):
            
            if y1 + j >= image_height(pixals):
                continue
            
            pixals[x1+i][y1+j] = color

    return pixals

def pixalate(pixals,width,height):
    x1 = 0;x2 = width
    while(x1 < image_width(pixals)):
        y1 = 0;y2 = height
        while(y1 < image_height(pixals)):
            color = average_color(crop_image(pixals,x1,x2,y1,y2))
            pixals = color_in(pixals,color,width,height,x1,y1)
            y1 += height; y2 += height
        x1 += width; x2 += width
    return pixals

def find_nearest_color(color,colors,directory):
    os.chdir(directory)
    min_distance = 10000
    for images in os.listdir(directory):
        distance = np.sqrt((colors[images]['red']-color[0])**2 + (colors[images]['green']-color[1])**2 + (colors[images]['blue']-color[2])**2)
        if distance < min_distance:
            min_distance = distance
            location = images
        else:
            continue
    return location

#def find_nearest_color(color,colors,map,directory):
    os.chdir(directory)
    options = map[round(color[0]),round(color[1]),round(color[2])]
    min_distance = 10000
    for images in options:
        distance = np.sqrt((colors[images]['red']-color[0])**2 + (colors[images]['green']-color[1])**2 + (colors[images]['blue']-color[2])**2)
        if distance < min_distance:
            min_distance = distance
            location = images
        else:
            continue
    return location

def scale_down(image,width,height):
    size = (width,height)
    scale = cv2.resize(image, size, interpolation = cv2.INTER_AREA)
    return scale

def insert_image(image,insert,width,height,x1,y1):
    insert = cv2.imread(insert)
    insert = scale_down(insert,width,height)

    for i in range(width):

        if x1 + i >= image_width(image):
            continue

        for j in range(height):
            
            if y1 + j >= image_height(image):
                continue
            
            image[x1+i][y1+j] = insert[i][j]

    return image

def collage(image,width,height,colors,directory):
    x1 = 0;x2 = width
    while(x1 < image_width(image)):
        y1 = 0;y2 = height
        while(y1 < image_height(image)):
            color = average_color(crop_image(image,x1,x2,y1,y2))
            path = find_nearest_color(color,colors,directory)
            image = insert_image(image,path,width,height,x1,y1)
            y1 += height; y2 += height
        x1 += width; x2 += width
    return image

def hash_colors(colors):
    map = {}
    for item in colors:
        r = round(colors[item]["red"])
        g = round(colors[item]["green"])
        b = round(colors[item]["blue"])
        map[r,g,b] = {item}
    return map

width = 5
height = 5

file = "" #insert name of image to use for base

path = r'' #insert images folder loaction
directory = r'' #insert where to put edited images
base_directory = r'' #insert directory here

image = import_image(file)

#image = pixalate(image,width,height)

directory = edit_source_files(path,directory,base_directory)
colors = find_source_color(directory,base_directory)
map = hash_colors(colors)

image = collage(image,width,height,colors,directory)

cv2.imshow("picture",image)
cv2.waitKey(0) 
cv2.destroyAllWindows()  
