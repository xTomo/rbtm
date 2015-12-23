#!/usr/bin/python
"""
29.11.15 - Rustam
Configuration file for module "Experiment"
Contains web-addresses of storage, of web-page of adjustment(of tomograph), of tomograph,
also contains name of png-file, creating for storing current image during experiment,
finally contains time that tomograph waits for commands during advanced experiments with exec.

If REAL_TOMOGRAPH_STORAGE_WEBPAGE is set as False, it launches stub servers
for storage and web-page of adjustment
"""



REAL_TOMOGRAPH_STORAGE_WEBPAGE = True





if REAL_TOMOGRAPH_STORAGE_WEBPAGE == True:
    
    TOMO_ADDR = "172.17.0.1:10000"

    STORAGE_FRAMES_URI = "http://10.0.7.153:5006/storage/frames/post"
    STORAGE_EXP_START_URI = "http://10.0.7.153:5006/storage/experiments/create"
    STORAGE_EXP_FINISH_URI = "http://10.0.7.153:5006/storage/experiments/finish"

    WEBPAGE_URI = "http://109.234.34.140:5021/take_image"



else:
    import subprocess
    TOMO_ADDR = '188.166.73.250:10000'

    STORAGE_FRAMES_URI     = "http://localhost:5020/stub_storage"
    STORAGE_EXP_START_URI  = "http://localhost:5020/stub_storage"
    STORAGE_EXP_FINISH_URI = "http://localhost:5020/stub_storage"
    subprocess.Popen(["./experiment/stubs/stub_storage.py"])
    # launch stub storage server on port 5020 - just for recieving messages from 'experiment' and answering 'success'

    WEBPAGE_URI = "http://localhost:5021/stub_webpage"
    subprocess.Popen(["./experiment/stubs/stub_webpage.py"])
    # launch stub web-page server on port 5021 - just for recieving messages from 'experiment' and answering 'success'





FRAME_PNG_FILENAME = 'image.png'

TIMEOUT_MILLIS = 200000

MAX_EXPERIMENT_TIME = 100
# MAX_EXPERIMENT_TIME is currently used only in advanced experiments with exec
