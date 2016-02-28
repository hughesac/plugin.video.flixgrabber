import sys
import urllib
import urlparse
import xbmcgui
import xbmcaddon
import xbmcplugin
import netflix
import os
import subprocess
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from contextlib import contextmanager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import \
    staleness_of
from selenium.common.exceptions import StaleElementReferenceException     

video_url = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
profilename = sys.argv[4]
datadir = sys.argv[5]

class Action(object):
	ABORT					= 0 # Is this abort?
	LEFT                    = 1
	RIGHT                   = 2
	UP                      = 3
	DOWN                    = 4
	PAGE_UP                 = 5  # Channel Up on MCE remote
	PAGE_DOWN               = 6  # Channel Down on MCE remote
	SELECT_ITEM             = 7
	ACTION_HIGHLIGHT_ITEM   = 8
	PARENT_DIR              = 9
	PREVIOUS_MENU           = 10
	ACTION_SHOW_INFO        = 11
	PAUSE                   = 12
	STOP                    = 13
	ACTION_NEXT_ITEM        = 14  # Remote: >>|
	ACTION_PREV_ITEM        = 15  # Remote: <<|
	FORWARD                 = 77  # Remote: >>
	REWIND                  = 78  # Remote: <<
	NAV_BACK                = 92  # introduced in eden
	ACTION_SCROLL_UP        = 111
	ACTION_SCROLL_DOWN      = 112
	CONTEXT_MENU            = 117  # TV Guide on MCE remote
	HOME                    = 159  # kbd only
	END                     = 160  # kbd only

class PlayerWindow(xbmcgui.Window):
    def __init__(self, driver=None, flix=None, *args, **kwargs):
        
    	# WINDOW_FULLSCREEN_VIDEO  http://kodi.wiki/view/Window_IDs
    	self.window = xbmcgui.Window(12005)
        self.driver = driver
        self.flix = flix
        
        super(PlayerWindow, self).__init__(*args, **kwargs)
        
    def onAction(self, action):
            actionId = action.getId()
            xbmc.log( "action received: %s" % actionId )
            if actionId in (Action.PREVIOUS_MENU, Action.NAV_BACK, Action.STOP):
            	xbmc.log("received previous menu")
            	self.driver.quit()
            	self.close()				
            elif actionId in [Action.DOWN]:
                xbmc.log("received volume down")
                ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
            elif actionId in [Action.UP]:
                xbmc.log("received volume up")
                ActionChains(driver).send_keys(Keys.ARROW_UP).perform()
                
            elif actionId in [Action.SELECT_ITEM, Action.PAUSE]:
            	xbmc.log("received pause/play")
            	ActionChains(driver).send_keys(Keys.SPACE).perform()
                self.flix.click_continue_playing()
            	
            elif actionId in [Action.FORWARD, Action.RIGHT]:
            	xbmc.log("received seek forward")			
            	ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ARROW_RIGHT).key_up(Keys.SHIFT).perform()
            	
            elif actionId in [Action.REWIND, Action.LEFT]:
            	xbmc.log("received seek back")
            	ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ARROW_LEFT).key_up(Keys.SHIFT).perform()				
                
flix = netflix.Netflix(username, password, profilename, datadir)
driver = flix.get_driver()
driver.get(video_url)
# Move the mouse so the cursor is hidden
ActionChains(driver).move_by_offset(1, 1).perform()  

	    
window = PlayerWindow(driver=driver, flix=flix)

window.doModal()
del window

