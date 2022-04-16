import os
import json
import subprocess

import pandas as pd
import ffmpeg


folder_to_search = '/media/' #'/mnt/SPACE/Movies/Youtube/'
json_info_file = '/mnt/INFO/Transcode_info.json'

extensions = ('.avi', '.mkv', '.wmv', '.mp4', '.mpg', '.mpeg', '.mov', '.m4v')

def findExt(folder):
    matches = []
    return [os.path.join(r, fn)
        for r, ds, fs in os.walk(folder) 
        for fn in fs if fn[fn.rfind('.'):].lower() in extensions]

def Transcode(file):
    #print(file)
    Start = os.path.getsize(file)
    name = ""
    for nazev in file.split(".")[:-1]:
        name += nazev

    name = name.replace(" ", "\ ").replace("  ", " ")+"_transcode.mkv"
    file = file.replace(" ", "\ ")

    command = ("ffmpeg -n -i "+file+" -c:v libx265 -preset slow -x265-params crf=28:bframes=1 -c:a aac "+name) 

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print(process.returncode)
    End = os.path.getsize(name)
    print(Start, End)


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