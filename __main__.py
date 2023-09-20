import os
import csv
import time
import globals
import threading
from scraping_manager.web_scraping import WebScraping # >>> MY MODULE UPDATED

# Initial values for proxy
globals.current_proxy = {
    "id": 0,
    "ip": "",
    "port": ""
}

# Get proxy list from file
proxy_path = os.path.join (os.path.dirname(__file__), "proxy_list.csv")
with open (proxy_path) as csv_file:
    csv_reader = csv.reader(csv_file)
    globals.proxy_list = list (csv_reader)
    
def end_running ():
    """ Set global running status to False
    """
    
    globals.running = False

def audiomack_validation (scraper):
    """Detect error loading the audiomack playlist

    Returns:
        bool: return True if there isn't an error
    """

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

def audiomack_play (scraper, thread_num):
    """ Play the audiomack playlist and wait until it end
    """

    print (f"Thread: {thread_num} Playing playlist...")
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
        continue
                
    
    print (f"Thread: {thread_num} Playlist ended.")

def get_chrome ():

    # Get the next proxy from list
    proxy_id = globals.current_proxy["id"] + 1
    globals.current_proxy["id"] = proxy_id
    globals.current_proxy["ip"] = globals.proxy_list[proxy_id][0]
    globals.current_proxy["port"] = globals.proxy_list[proxy_id][1]

    scraper = WebScraping(
        headless=False, 
        proxy_server=globals.current_proxy["ip"], 
        proxy_port=globals.current_proxy["port"]
    )

    return scraper
        
def run_bot (thread_num):
    """Project flow: open videos and watch"""

    link = "https://audiomack.com/dapoloman/album/ghetto-goblins-mixtape-volume-1"

    # Open page since found a valid proxy
    while globals.current_proxy["id"] < len (globals.proxy_list):

        proxy_found = False
        try:
            # Open chrome instance with new proxy
            scraper = get_chrome()

            # Show current proxy
            print (f'Thread: {thread_num}, Proxy {globals.current_proxy["id"]}, Address: {globals.current_proxy["ip"]}:{globals.current_proxy["port"]}')

            # Try to open page and catch if error happend
            scraper.set_page (link, time_out=60)
            
        except Exception as e:
            # >>> DEBUG WHEN THREAD / CHROME CRASH
            print (f"Thread: {thread_num} Error: {e}")
            
            # Try again
            scraper.end_browser()
            continue
        else:

            # Detect internal error in the page and play video / audio
            if "audiomack" in link:
                correct_load = audiomack_validation (scraper)
                if correct_load:
                    audiomack_play (scraper, thread_num)
                    proxy_found = True
                    break
                else:
                    # Try again
                    scraper.end_browser()
                    continue
    
    if not proxy_found: 
        print (f"Thread: {thread_num} No more proxies in file.")


if __name__ == '__main__':

    bots_num = 3
    
    while globals.running:
        
        # Sample killing thread
        thread_obj = threading.Thread (target=end_running)
        thread_obj.start ()

        # Start all threads
        thread_objs = []
        for thread_num in range (1, bots_num + 1):

            # Wait time between each thread
            time.sleep (10)

            # Start thread and save in list
            thread_obj = threading.Thread (target=run_bot, args=(thread_num,))
            thread_obj.start ()
            thread_objs.append (thread_obj)

        # Wait to end all threads
        for thread_obj in thread_objs:
            thread_obj.join ()
