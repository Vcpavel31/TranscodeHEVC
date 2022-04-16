import os
import json
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
        Start = os.path.getsize(data.file)

        command = ("ffmpeg -n -i "+data.file+" -c:v libx265 -preset slow -x265-params crf=28:bframes=1 -c:a aac "+data.name) 
        proc = subprocess.Popen(
            command,             #call something with a lot of output so we can see it
            shell=True,
            stdout=subprocess.PIPE
        )

        for line in iter(proc.stdout.readline,''):
            time.sleep(1)                           # Don't need this just shows the text streaming
            yield line.rstrip() + '<br/>\n'

        #proc.wait()
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

def Transcode(file):
    #print(file)
    
    name = ""
    for nazev in file.split(".")[:-1]:
        name += nazev

    data.name = name.replace(" ", "\ ").replace("  ", " ")+"_transcode.mkv"
    data.file = file.replace(" ", "\ ")

    app.run(debug=True, port=5000, host='0.0.0.0')

    """process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    Return_Code = process.returncode
    print(Return_Code)
    if(Return_Code != 0):
        os.remove(name)
        print("Error: "+file)
    else:
        End = os.path.getsize(name)
        print(Start, End)
        # Move "name" to "file"
        os.remove(file)
        os.rename(name, file)"""


def main():
    
    video_files = findExt(folder_to_search)
    for file in video_files:
        if("Plex Versions" in file or "_transcode" in file):
            pass
        else:
            #print(file)
            try:
                fp = ffmpeg.probe(file)
                print(json.dumps(fp, indent=4, sort_keys=True))

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
                        print("Wrong codec: "+file+" "+stream['codec_type']+" "+stream['codec_name'])
                        Encode = 1

                if(Encode == 1):
                    Transcode(file)

            except Exception as e:
                print(e)
                pass

if __name__ == '__main__':
    main()