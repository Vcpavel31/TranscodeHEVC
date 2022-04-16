import os
import json
from re import ASCII
import subprocess
import time

import pandas as pd
import ffmpeg
import flask

app = flask.Flask(__name__)

class DataStore():
    name = None
    file = None

data = DataStore()

folder_to_search = '/media/' #'/mnt/SPACE/Movies/Youtube/'
json_info_file = '/mnt/INFO/Transcode_info.json'

extensions = ('.avi', '.mkv', '.wmv', '.mp4', '.mpg', '.mpeg', '.mov', '.m4v')

def findExt(folder):
    return [os.path.join(r, fn)
        for r, ds, fs in os.walk(folder) 
        for fn in fs if fn[fn.rfind('.'):].lower() in extensions]

@app.route('/yield')
def index():
    def inner():
        print(data.file.replace("\ ", " "))
        Start = os.path.getsize(data.file.replace("\ ", " "))

        command = ("ffmpeg -stats_period 1 -hide_banner -nostats -n -i "+data.file+" -c:v libx265 -preset slow -x265-params crf=28:bframes=1 -c:a aac "+data.name) 
        proc = subprocess.Popen(
            command,             #call something with a lot of output so we can see it
            shell=True,
            stdout=subprocess.PIPE
        )

        for line in iter(proc.stdout.readline,''):
            #time.sleep(1)                           # Don't need this just shows the text streaming
            yield line.rstrip().decode("ascii") + '<br/>\n'

        proc.wait()
        Return_Code = proc.returncode
        print(Return_Code)
        if(Return_Code != 0):
            os.remove(data.name)
            print("Error: "+data.file)
        else:
            End = os.path.getsize(data.name)
            print(Start, End)
            # Move "name" to "file"
            os.remove(data.file)
            os.rename(data.name, data.file)

    return flask.Response(inner(), mimetype='text/html')  # text/html is required for most browsers to show th$

def Transcode():
    
    name = ""
    for nazev in data.file.split(".")[:-1]:
        name += nazev

    data.name = name.replace("  ", " ")+"_transcode.mkv"
    #app.run(debug=True, port=5000, host='0.0.0.0')

    Start = os.path.getsize(data.file)
    #-hide_banner -loglevel error -nostats
    command = ("ffmpeg  -n -i "+data.file.replace(" ", "\ ")+" -c:v libx265 -preset slow -x265-params crf=28:bframes=1 -c:a aac "+data.name.replace(" ", "\ ")) 
    proc = subprocess.Popen(
        command,             #call something with a lot of output so we can see it
        shell=True,
        stdout=subprocess.PIPE
    )
    proc.wait()
    Return_Code = proc.returncode
    print(Return_Code)
    if(Return_Code != 0):
        os.remove(data.name)
        print("Error: "+data.file)
    else:
        End = os.path.getsize(data.name)
        print(Start, End)
        # Move "name" to "file"
        os.remove(data.file)
        os.rename(data.name, data.file)

def main():
    
    video_files = findExt(folder_to_search)
    for file in video_files:
        if("Plex Versions" in file or "_transcode" in file):
            pass
        else:
            try:
                fp = ffmpeg.probe(file)
                #print(json.dumps(fp, indent=4, sort_keys=True))

                if(file.lower().replace(" ", "").endswith(".mkv")):
                    Encode = 0
                else:
                    print("File is not MKV")
                    Encode = 1
                
                for stream in fp['streams']:
                    if(stream['codec_type'] == "video" and stream['codec_name'] == "hevc"): 
                        pass
                    elif(stream['codec_type'] == "audio" and stream['codec_name'] == "aac"): 
                        pass
                    elif(stream['codec_type'] == "subtitle"): # and stream['codec_name'] == "ass"
                        pass
                    else:
                        #print text in red color
                        print("\033[91m"+"Wrong codec: "+file+" "+stream['codec_type']+"/"+stream['codec_name']+"\033[0m")
                        
                        Encode = 1

                if(Encode == 1):
                    data.file = file
                    Transcode()
                else:
                    pass

            except Exception as e:
                print(e)
                pass

if __name__ == '__main__':
    main()