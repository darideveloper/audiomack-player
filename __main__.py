import os
import csv
import time
import globals
import threading
from scraping_manager.automate import Web_scraping

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

def audiomack_validation (scraper):
    """Detect error loading the audiomack playlist

    Returns:
        bool: return True if there isn't an error
    """

    # Check if the page correct loaded
    selector_sample = "nav.site-sidebar__widget.widget > ul > li:nth-child(1) > a"
    sample_text = scraper.get_text (selector_sample)
    if not sample_text:
        return False

    # Internal 404 error
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
    selector_play = 'button[aria-label="Play album"]'
    scraper.click (selector_play)
    time.sleep (20)
    scraper.refresh_selenium ()

    # Detect when playlist end
    while True:
        selector_playing_svg = "svg.tracklist__track-icon"
        svg_class = scraper.get_attrib (selector_playing_svg, "class")
        if svg_class:
            time.sleep (5)
            continue
        else:
            break
    
    print (f"Thread: {thread_num} Playlist ended.")

def get_chrome ():

    # Get the next proxy from list
    proxy_id = globals.current_proxy["id"] + 1
    globals.current_proxy["id"] = proxy_id
    globals.current_proxy["ip"] = globals.proxy_list[proxy_id][0]
    globals.current_proxy["port"] = globals.proxy_list[proxy_id][1]

    scraper = Web_scraping(web_page="", 
                            headless=False, 
                            proxy_server=globals.current_proxy["ip"], 
                            proxy_port=globals.current_proxy["port"])

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
            scraper.set_page (link, time_out=30)
        except:
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
