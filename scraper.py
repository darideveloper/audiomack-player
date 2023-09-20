import os
import csv
import time
import random
import globals
import threading
from scraping_manager.web_scraping import WebScraping # >>> MY MODULE UPDATED

# Initial values for proxy
globals.current_proxy = {
    "id": 0,
    "ip": "",
    "port": ""
}

def audiomack_validation (scraper):
    """Detect error loading the audiomack playlist

    Returns:
        bool: return True if there isn't an error
    """

    try:

        # Check if the page correct loadedç
        # >>> SELECTOR UPDATED
        selector_track = ".tracklist__track-wrap"
        sample_text = scraper.get_text (selector_track)
        if not sample_text:
            return False

        # Internal 404 error
        # >>> SELECTOR UPDATED
        selector_error = ".error-404__title"
        error = scraper.get_text (selector_error)
        if error == "404":
            return False
        else:
            return True
    except: 
        return False

def audiomack_play (scraper, thread_num):
    """ Play the audiomack playlist and wait until it end
    """

    message = f"Thread: {thread_num} Playing playlist..."
    print (message)
    globals.message = message
    
    # >>> SELECTOR UPDATED
    selector_play = "[class*='MusicActionButton']"
    scraper.click (selector_play)
    time.sleep (20)
    scraper.refresh_selenium ()

    # >>> SELECTOR UPDATED
    selector_playing_svg = "svg.tracklist__track-icon"
    
    # Detect when playlist end
    while True:
        
        if not globals.running:
            break
        
        # >>> Check two times if is plaing
        # >>> FIRST CHECK
        try:
            svg_class_a = scraper.get_attrib (selector_playing_svg, "class")
            if not svg_class_a:
                
                # WAIT BEFORE SECOND CHECK
                time.sleep (5)
                
                # >>> SECOND CHECK
                svg_class_b = scraper.get_attrib (selector_playing_svg, "class")
            
                # >>> END PLAYLIST
                if not svg_class_b:
                    break
            
            # >>> WAIT BEFORE CHECK AGAIN
            time.sleep (5)
        except:
            pass
    
        continue
    
    message = f"Thread: {thread_num} Playlist ended."
    print (message)
    globals.message = message

def get_chrome ():

    # Get ramdom proxy from file
    random_proxy = random.choice (globals.proxy_list)
    globals.current_proxy["ip"] = random_proxy[0]
    globals.current_proxy["port"] = random_proxy[1]

    scraper = WebScraping(
        headless=False, 
        proxy_server=globals.current_proxy["ip"], 
        proxy_port=globals.current_proxy["port"]
    )

    return scraper
        
def run_bot (thread_num:int, link:str):
    """Project flow: open videos and watch
    
    Args:
        thread_num (int): Thread number
        link (str): Link to open
    """

    link = f"https://audiomack.com/{link}"
    
    try:
        # Open chrome instance with new proxy
        scraper = get_chrome()

        # Show current proxy
        message = f'Thread: {thread_num}, Proxy {globals.current_proxy["id"]}, Address: {globals.current_proxy["ip"]}:{globals.current_proxy["port"]}'
        print (message)
        globals.message = message

        # Try to open page and catch if error happend
        scraper.set_page (link, time_out=60)
        
    except Exception as e:
        # >>> DEBUG WHEN THREAD / CHROME CRASH
        message = f"Thread: {thread_num} Error: {e}"
        print (message)
        globals.message = message
        
    else:
        
        if globals.running:

            # Detect internal error in the page and play video / audio
            correct_load = audiomack_validation (scraper)
            if correct_load and globals.running:
                audiomack_play (scraper, thread_num)

def run_bots (bots:int, link:str):
    """ Sart bots with threads 
    
    Args:
        bots (int): Number of bots to run
        link (str): Link to open
    """
    
    # Load proxies from file when start
    proxy_path = os.path.join (os.path.dirname(__file__), "proxies.csv")
    with open (proxy_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        globals.proxy_list = list (csv_reader)
    
    while globals.running:
        
        # Kill all chrome process from terminal silently
        os.system ("taskkill /f /im chrome.exe >nul 2>&1")

        globals.message = "opening bots..."

        # Start all threads
        thread_objs = []
        for thread_num in range (1, bots + 1):

            # Wait time between each thread
            time.sleep (3)

            # Start thread and save in list
            thread_obj = threading.Thread (target=run_bot, args=(thread_num, link))
            thread_obj.start ()
            thread_objs.append (thread_obj)

        # Wait to end all threads
        for thread_obj in thread_objs:
            thread_obj.join ()
            
    globals.ended = True