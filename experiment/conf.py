#!/usr/bin/python

"""
Configuration file for module "Experiment"
Contains web-addresses of storage, of web-page of adjustment(of tomograph), of tomograph,
also contains name of name of png-file, creating for storing current image during experiment,
finally contains time that tomograph waits for commands
"""


STORAGE_IS_FICTITIOUS = True

WEBPAGE_OF_ADJUSTMENT_IS_FICTITIOUS = True

TOMOGRAPH_IS_FICTITIOUS = True




FRAME_PNG_FILENAME = 'image.png'

TIMEOUT_MILLIS = 200000

MAX_EXPERIMENT_TIME = 100








if STORAGE_IS_FICTITIOUS:
    STORAGE_FRAMES_URI = "http://109.234.34.140:5020/fictitious-storage"
    STORAGE_EXP_START_URI = "http://109.234.34.140:5020/fictitious-storage"
    STORAGE_EXP_FINISH_URI = "http://109.234.34.140:5020/fictitious-storage"
else:
    #STORAGE_URI = "http://188.166.66.37:5006/storage/frames/post"                     # To send frames
    #STORAGE_EXPERIMENT_URI = "http://188.166.66.37:5006/storage/experiments/post"     # To send experiment parameters
    STORAGE_FRAMES_URI = "http://109.234.34.140:5006/storage/frames/post"               # To send frames
    STORAGE_EXP_START_URI = "http://109.234.34.140:5006/storage/experiments/create"     # To send experiment parameters
    STORAGE_EXP_FINISH_URI = "http://109.234.34.140:5006/storage/experiments/finish"    # To send messages about experiment stops

if WEBPAGE_OF_ADJUSTMENT_IS_FICTITIOUS:
    WEBPAGE_URI = "http://109.234.34.140:5021/take_image"
else:
    WEBPAGE_URI = "http://109.234.34.140:5021/take_image"

if TOMOGRAPH_IS_FICTITIOUS:
    TOMO_ADDR = '188.166.73.250:10000'
else:
    TOMO_ADDR = 'localhost:10000'
