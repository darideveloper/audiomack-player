import os
import time
import globals
import PySimpleGUI as sg
from scraper import run_bots
from threading import Thread

CURRENT_FOLDER = os.path.dirname(__file__)

def gui (): 
    """Main function of the project with gui
    """
                
    # Set theme
    sg.theme("DarkAmber")

    # Main screedn layout
    layout = [
        [
            sg.Text ("https://audiomack.com/", size=(18,1)),
            sg.InputText (size=(30,1), key="link", default_text="dapoloman/album/ghetto-goblins-mixtape-volume-1"),
        ],
        [
            sg.Text ("Bots number", size=(18,1)),
            sg.InputText (size=(30,1), key="bots", default_text="3"),
        ],
        [
            sg.Button("Run", size=(18,1), key="run"),  
            sg.Button("Proxies", size=(12,1), key="proxies"),  
            sg.Button("Exit", size=(12,1), key="quit"),
        ],
    ]
    
    # Create window
    window = sg.Window("audiomack player", layout, no_titlebar=False)
    
    
    thread_obj = None
    while True:    
        
        reopen = False
    
        event, values = window.read()
                
        # RUN BUTTONS                 
                   
        # End program when close windows
        if event == sg.WIN_CLOSED or event == 'quit':
            break
        
        if event == "run": 
            
            globals.running = True
            globals.ended = False
            
            # Start bots in new thread
            thread_obj = Thread (target=run_bots, args=(int(values["bots"]), values["link"]))
            thread_obj.start ()
            
            # Open new windows with the text: loading
            reopen = True
            
            # Loading screedn layout
            layout = [
                [
                    sg.Text ("Loading...", size=(40,1), key="status"),
                ],
                [
                    sg.Button("Stop", size=(40,1), key="stop"),  
                ],
            ]
            
            # Create loading window
            window_loading = sg.Window("audiomack player loading", layout, no_titlebar=False)
            
            while True:
                            
                event, _ = window_loading.read(timeout=500)
                
                # Update status
                window_loading["status"].update (globals.message)
                
                if event == sg.WIN_CLOSED or event == "stop": 
            
                    globals.message = "Stopping bots..."
            
                    # Change running status
                    globals.running = False
                    
                    # Kill all chrome process from terminal silently
                    os.system ("taskkill /f /im chrome.exe >nul 2>&1")
                    
                # Wait to end thread
                if globals.ended: 
                    break
                    
            thread_obj.join()
            window_loading.close()
            
        if event == "proxies":
            
            # Open proxies file with notepad
            proxies_path = os.path.join (CURRENT_FOLDER, "proxies.csv") 
            os.system (f"notepad.exe {proxies_path}")
                            
    # End window
    window.close()
    
    # Reopen window after changes
    if reopen: 
        gui()