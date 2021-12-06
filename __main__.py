import os
import csv
from scraping_manager.automate import Web_scraping

# Global variables for control the last and the current proxy

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

def get_chrome ():

    global current_proxy

    # Get the next proxy from list
    proxy_id = current_proxy["id"] + 1
    current_proxy["id"] = proxy_id
    current_proxy["ip"] = proxy_list[proxy_id - 1][0]
    current_proxy["port"] = proxy_list[proxy_id - 1][1]

    scraper = Web_scraping(web_page="", 
                            headless=False, 
                            proxy_server=current_proxy["ip"], 
                            proxy_port=current_proxy["port"])

    return scraper
        

def main ():
    """Project flow: open videos and watch"""

    global current_proxy

    link = "https://audiomack.com/dapoloman/album/ghetto-goblins-mixtape-volume-1"

    # Open page since found a valid proxy
    while True:
        try:
            # Open chrome instance with new proxy
            scraper = get_chrome()

            # Show current proxy
            print (f'Proxy id: {current_proxy["id"]}, Address: {current_proxy["ip"]}:{current_proxy["port"]}')

            # Try to open page
            scraper.set_page (link, time_out=60)
        except:
            # Try again
            scraper.kill()
            continue
        else:

            # Check if the page correct load
            selector_sample = "nav.site-sidebar__widget widget > ul > li:nth-child(1) > a"
            sample_text = scraper.get_text (selector_sample)
            if sample_text:
                # End loop (valid proxy found)
                break
            else:
                continue

    input ("end?")




if __name__ == '__main__':
    main()