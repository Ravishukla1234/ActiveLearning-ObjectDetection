import os
os.system('pip install -U sagemaker')
os.system('pip install -U boto3')
os.system('pip install -U pandas')
os.system('pip install -U botocore')
os.system('pip install -U s3fs')
os.system('pip install matplotlib')

import pickle
import pandas as pd
import numpy as np

import sagemaker
import boto3
import json
import uuid
import time 

import sagemaker
import botocore






def read_manifest_file(file_path):
    with open(file_path, 'r') as f:
        output = [json.loads(line.strip()) for line in f.readlines()]
        return output
def visualize_detection(img_file, dets, classes=[], thresh=0.6):
        """
        visualize detections in one image
        Parameters:
        ----------
        img : numpy.array
            image, in bgr format
        dets : numpy.array
            ssd detections, numpy.array([[id, score, x1, y1, x2, y2]...])
            each row is one object
        classes : tuple or list of str
            class names
        thresh : float
            score threshold
        """
        import random
        ##import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        img = mpimg.imread(img_file)
        #plt.imshow(img)
        height = img.shape[0]
        width  = img.shape[1]
        depth  = img.shape[2]
        colors = dict()
        num_detections = 0
        for det in dets:
            (klass, score, x0, y0, x1, y1) = det
            if score < thresh:
                continue
            num_detections += 1
            cls_id = int(klass)
            if cls_id not in colors:
                colors[cls_id] = (random.random(), random.random(), random.random())
            xmin = int(x0 * width)
            ymin = int(y0 * height)
            xmax = int(x1 * width)
            ymax = int(y1 * height)
            dic = {'xmin':xmin, 'xmax':xmax,'ymin':ymin,'ymax':ymax,"height":height,'width':width,"depth":depth,'class_id':cls_id,'confidence':score}
           # print("box ==({},{})({},{})({},{})({},{})".format(xmin,ymin,xmin,ymax,xmax,ymin,xmax,ymax ))
           # rect = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fill=False,
           #                      edgecolor=colors[cls_id], linewidth=3.5)
            #plt.gca().add_patch(rect)
            class_name = str(cls_id)
            if classes and len(classes) > cls_id:
                class_name = classes[cls_id]
            #print('{},{}'.format(class_name,score))
            #plt.gca().text(xmin, ymin - 2,
             #               '{:s} {:.3f}'.format(class_name, score),
              #              bbox=dict(facecolor=colors[cls_id], alpha=0.5),
              #                      fontsize=12, color='white')

        print('Number of detections: ' + str(num_detections))
       # plt.show()
        return dic
    
    
if __name__ == '__main__':
    
    ########################################################################
    local_path = '/opt/ml/processing/out_images'
    unlabeled_manifest = '/opt/ml/processing/unlabeled_manifest/unlabeled.manifest'
    image_path = '/opt/ml/processing/images'
    manifest_file = '/opt/ml/processing/output/newlabelled.manifest' #Output
    OBJECT_CATEGORIES = ['bird']
    thresh = 0.4
    
    ########################################################################
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(local_path) if isfile(join(local_path, f))]
    manifest = read_manifest_file(unlabeled_manifest)

    

    with open(manifest_file, 'w') as outfile:
        for element in manifest:
            s3path = element['source-ref']
            file_name = s3path.split('/')[-1]
            image_file_name = image_path+'/'+file_name 
            if(file_name+".out" in onlyfiles):
                print(file_name)
                with open(local_path+"/"+file_name+".out" ,'r') as f:
                    file = f.read()
                    detections = json.loads(file)
                    dic = visualize_detection(image_file_name, detections['prediction'], OBJECT_CATEGORIES, thresh)
                    #print(dic)
                    out={}
                    out["source-ref"] = element["source-ref"]
                    out['id'] = element['id']
                    out["labelling-job-clone"] = {"image_size":[{"width":dic["width"], "height":dic["height"],"depth":dic["depth"]}]}       
                    out['annotations'] = [{"class_id": dic["class_id"],
                    "top": dic["ymin"],
                    "left": dic["xmin"],
                    "height": dic["height"],
                    "width": dic["width"]}]
                    out["class-map"]= {"0": "Bird"}
                    out["type"]: "groundtruth/object-detection"
                    out["confidence"]=dic["confidence"]
                    out["human-annotated"] =  "no"
                    out["creation-date"] = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
                    out["job-name"]: "labeling-job/object-detection"
                    print(str(out))
                    outfile.write(str(out)+'\n') 

    
    
    
    