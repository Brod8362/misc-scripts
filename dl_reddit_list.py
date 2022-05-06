#!/bin/python3
import queue
import sys
import requests
import json
import subprocess
import time
import os
#a script that downloads a list of reddit post ids provided by stdin
# uses yt-dlp 

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID", "")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def erase_line() -> None:
    print("\033[2K", end = "")

def progress_bar(width: int, current: int, total: int, fill="▓", empty="░") -> str:
    amt = int((current/total)*width)
    return (fill*amt) + (empty*(width-amt))

def format_time(start, end = None) -> str:
    if end == None:
        end = time.time()
    elapsed = int(end - start)
    return f"{elapsed//60}m{elapsed%60:02}s"

def status(message: str, progress: int, size: int, start_time, extra: dict = None) -> None:
    erase_line()
    ex = ""
    for k in extra:
        ex += f"{k}={extra[k]} "
    eta_text = "--:--"
    if (progress > 30 or progress/size > 0.05):
        time_per_post = (time.time() - start_time)/progress #time per post on avg, in seconds
        eta_text = format_time(0, int(time_per_post*(size-progress)))
    print(f"\r[{progress_bar(40, progress, size)}] {progress}/{size} {int((progress/size)*100)}% {format_time(start_time)} eta {eta_text} {bcolors.HEADER}{ex}{bcolors.OKCYAN}{message}{bcolors.ENDC}", end="")

def log(message: str, color: str) -> None:
    erase_line()
    print(f"\r{color}{message}{bcolors.ENDC}")

def log_error(message: str) -> None:
    erase_line()
    log(message, bcolors.FAIL)

def log_info(message:str) -> None:
    erase_line()
    log(message, bcolors.OKGREEN)

def post_info(id: str): #tuple[str,str,str]
    data = requests.get(f"https://www.reddit.com/comments/{id}/.json", headers={"User-Agent":"u/Brod8362 post DL"})
    if data.status_code != 200:
        log_error(f"Failed to fetch {id}: received response code {data.status_code}")
        return None
    js = json.loads(data.text)
    subreddit = js[0]["data"]["children"][0]["data"]["subreddit"]
    link = js[0]["data"]["children"][0]["data"]["url"]
    title = js[0]["data"]["children"][0]["data"]["title"]
    text_post = js[0]["data"]["children"][0]["data"]["is_self"]
    return (subreddit, link, title, text_post)

def download_direct(link: str, path: str) -> bool:
    data = requests.get(link)
    if data.status_code == 200:
        ext = link.split(".")[-1]
        fd = open(path+"."+ext, 'wb')
        fd.write(data.content)
        fd.close()
    return data.status_code == 200

def album_progress(step: int, size: int, id: str):
    erase_line()
    print(f"\r[{progress_bar(30, step, size)}] {bcolors.OKBLUE}{step}/{size} Downloading album {id}{bcolors.ENDC}", end="")

def download_imgur_album(link: str, base_path: str) -> bool:
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    sections = link.split("/")
    album_id = sections[sections.index("a")+1]
    data = requests.get(f"https://api.imgur.com/3/album/{album_id}.json", headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"})
    if data.status_code != 200:
        return False
    js = json.loads(data.text)
    failed = 0
    size = len(js["data"]["images"])
    for i in range(0, size):
        album_progress(i, size, album_id)
        url = js["data"]["images"][i]["link"]
        if not download_direct(url, base_path+f"/{i}"):
            failed +=1
        i+=1

    if failed:
        log_error(f"{failed} failed downloads in album {album_id}")

    return True

def download(link: str, sr: str, id: str, name: str) -> bool:
    path = f"srdl/{sr}"
    replacements = {
        ' ': '_',
        '"': '',
        '\'': '',
        '.': '',
        '/': '',
        '\\': ''
    }
    for orig, new in replacements.items():
        name = name.replace(orig, new)
    fname = path+f"/{id}_{name[:128]}"
    if not os.path.exists(path):
        os.makedirs(path)
    #TODO: imgur albums, gyfact
    direct_ext = ("mp4", "mkv", "png", "jpg", "jpeg", "gifv", "gif", "webm")
    try:
        if link.endswith(direct_ext):
            return download_direct(link, fname)
        elif "imgur.com/a/" in link:
            return download_imgur_album(link, fname)
        elif "imgur.com/" in link:
            #imgur non-direct image link
            return False
        else: #attempt yt-dlp 
            command =   ["yt-dlp", "-q", "-o", fname+".%(ext)s", link]
            proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            proc.wait()
            if proc.returncode != 0:
                log_error(f"Failed to download URL: {link}")
            return proc.returncode == 0
    except:
        return False

def main():
    post_queue: queue.Queue = queue.Queue()
    csv_mode = "-csv" in sys.argv
    line = 0
    for data in sys.stdin:
        if csv_mode:
            if line != 0:    
                post_id = data.split(",")[0]
                post_queue.put(post_id)
        else:
            split = data.split("/")
            post_id = split[split.index("comments")+1]
            post_queue.put(post_id)
        line+=1
    
    progress = 0
    init_size = post_queue.qsize()
    fails = {}
    ex_data = {}
    start_time = time.time()
    while post_queue.qsize() > 0:
        time.sleep(0.25)
        progress += 1
        id = post_queue.get()
        status(f"Fetching {id}", progress, init_size, start_time, ex_data)
        ret = post_info(id)
        if ret:
            (subreddit, link, title, text) = ret
            status(f"Downloading {title[:50]}", progress, init_size, start_time, ex_data)
            if text:
                ex_data["no_media"] = ex_data.get("no_media", 0)+1
                status(f"{id} has no media", progress,init_size, start_time, ex_data)
                fails[id] = "no_media"
                continue
            if not download(link, subreddit, id, title):
                status(f"Failed to download {id}", progress,init_size, start_time, ex_data)
                ex_data["dl_err"] = ex_data.get("dl_err", 0)+1
                fails[id] = "dl_err"
                continue 
        else:
            status(f"Failed to fetch {id}", progress,init_size,start_time, ex_data)
            ex_data["fetch_err"] = ex_data.get("fetch_err", 0)+1
            fails[id] = "fetch_err"

    if len(fails) > 0:
        f = open("fails.csv", 'w')
        for key in fails:
            f.write(f"{key},{fails[key]}\n")
        f.close()

    log_info(f"\rCompleted in {format_time(start_time)}")


if __name__ == "__main__":
    main()