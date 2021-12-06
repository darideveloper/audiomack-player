import os
import csv
import time
from scraping_manager.automate import Web_scraping

scraper = None

# Initial values for proxy
current_proxy = {
    "id": 0,
    "ip": "",
    "port": ""
}

# Get proxy list from file
proxy_path = os.path.join (os.path.dirname(__file__), "proxy_list.csv")
with open (proxy_path) as csv_file:
    csv_reader = csv.reader(csv_file)
    proxy_list = list (csv_reader)

def audiomack_validation ():
    """Detect error loading the audiomack playlist

    Returns:
        bool: return True if there isn't an error
    """

    global scraper

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

def audiomack_play ():
    """ Play the audiomack playlist and wait until it end
    """

    global scraper

    print ("Playing playlist...")
    selector_play = 'button[aria-label="Play album"]'
    scraper.click (selector_play)
    time.sleep (5)
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
    
    print ("Playlist ended.")

def get_chrome ():

    # Get the next proxy from list
    proxy_id = current_proxy["id"] + 1
    current_proxy["id"] = proxy_id
    current_proxy["ip"] = proxy_list[proxy_id][0]
    current_proxy["port"] = proxy_list[proxy_id][1]

    scraper = Web_scraping(web_page="", 
                            headless=False, 
                            proxy_server=current_proxy["ip"], 
                            proxy_port=current_proxy["port"])

    return scraper
        
def main ():
    """Project flow: open videos and watch"""

    global scraper

    link = "https://audiomack.com/dapoloman/album/ghetto-goblins-mixtape-volume-1"

    # Open page since found a valid proxy
    while current_proxy["id"] < len (proxy_list):

        proxy_found = False
        try:
            # Open chrome instance with new proxy
            scraper = get_chrome()

            # Show current proxy
            print (f'Proxy {current_proxy["id"]}, Address: {current_proxy["ip"]}:{current_proxy["port"]}')

            # Try to open page and catch if error happend
            scraper.set_page (link, time_out=30)
        except:
            # Try again
            scraper.end_browser()
            continue
        else:

            # Detect internal error in the page and play video / audio
            if "audiomack" in link:
                correct_load = audiomack_validation ()
                if correct_load:
                    audiomack_play ()
                    proxy_found = True
                    break
                else:
                    # Try again
                    scraper.end_browser()
                    continue
    
    if not proxy_found: 
        print ("No more proxies in file.")



            





if __name__ == '__main__':
    main()