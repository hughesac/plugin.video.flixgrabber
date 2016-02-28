import sys
import urllib
import urlparse
import xbmcgui
import xbmcaddon
import xbmcplugin
import netflix
import pickle
import os
import subprocess
import shutil


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
addonId = addon.getAddonInfo('id')
username = addon.getSetting("username")
password = addon.getSetting("password")
scriptFileSysPath = xbmc.translatePath('special://home/addons/'+addonId)
mode = args.get('mode', None)

PICKLE_FILE = os.path.join(scriptFileSysPath, "netflix.pickle")
PROFILES_DICT_KEY = "profiles"

CHROME_USER_DATA_PATH = xbmc.translatePath('special://home/addons/%s/ChromeProfile' % addonId)

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def init():
    if os.access(PICKLE_FILE, os.R_OK):
        xbmc.log("Loading data from pickle")
        netflixDict = pickle.load(open(PICKLE_FILE, "rb"))
        
    else:
        xbmc.log("Getting fresh data")
        netflixDict = {}
        netflixDict[PROFILES_DICT_KEY] = netflix.Netflix(username, password, profilename=None, datadir=CHROME_USER_DATA_PATH).get_profiles()
        # Save the netflix data for use later
        pickle.dump(netflixDict, open(PICKLE_FILE, "wb"))            
    
    for name in netflixDict[PROFILES_DICT_KEY]:
        xbmc.log("adding: " + name)
        url = build_url({'mode': 'profile', 'profilename': name})
        li = xbmcgui.ListItem(name, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)        
        
    xbmcplugin.endOfDirectory(addon_handle)            

def profile_selection():
    profilename = args['profilename'][0]
    
    if os.access(PICKLE_FILE, os.R_OK):
    
        netflixDict = pickle.load(open(PICKLE_FILE, "rb"))
            
        if (not netflixDict.has_key(profilename)) or  \
           (len(netflixDict[profilename].items()) == 0): 
            xbmc.log("Getting fresh data")
            netflixDict[profilename] = netflix.Netflix(username, password, profilename, datadir=CHROME_USER_DATA_PATH).get_categories()            
            try:
                os.remove(PICKLE_FILE)
            except:
                pass        
             
            # Save the netflix data for use later
            pickle.dump(netflixDict, open(PICKLE_FILE, "wb"))
            
        for category, _ in netflixDict[profilename].items():
            url = build_url({'mode': 'category', 'profilename': profilename, 'category': category})
            li = xbmcgui.ListItem(category, iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)          
    xbmcplugin.endOfDirectory(addon_handle)
    
def category_selection():
    profilename = args['profilename'][0]
    category = args['category'][0]
    
#     scriptPath = xbmc.translatePath('special://home/addons/'+addonId+'/contextMenu.py')
#     url = build_url({'mode': 'clear_category', 'category' : category})
#     scriptCmd = 'XBMC.RunScript(%s, %s)' % (scriptPath, url)
#     commands = [("Refresh", scriptCmd, )]     
    
    if os.access(PICKLE_FILE, os.R_OK):
        netflixDict = pickle.load(open(PICKLE_FILE, "rb"))        
            
        if netflixDict.has_key(profilename):
            for title, flixUrl in netflixDict[profilename][category].items():
                url = build_url({'mode': 'play', 'profilename' : profilename, 'url': flixUrl})
                li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
#                 li.addContextMenuItems( commands )
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

    
def play():
    url = args['url'][0]
    profilename = args['profilename'][0]
    
    scriptPath = xbmc.translatePath('special://home/addons/'+addonId+'/player.py')
    xbmc.executebuiltin('XBMC.RunScript(%s, %s, %s, %s, %s, %s)' % (scriptPath, url, username, password, profilename, CHROME_USER_DATA_PATH))        
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def delete_cache():
    '''
    Delete the cached list of videos under each profile
    '''
    xbmc.log("delete_cache called")
    if os.access(PICKLE_FILE, os.R_OK):
        xbmc.log("Loading data from pickle")
        netflixDict = pickle.load(open(PICKLE_FILE, "rb"))
        for profilename in netflixDict[PROFILES_DICT_KEY]:
            if netflixDict.has_key(profilename):
                netflixDict.pop(profilename)
        
        os.remove(PICKLE_FILE)
    
        # Save the netflix data for use later
        pickle.dump(netflixDict, open(PICKLE_FILE, "wb"))         

    xbmcplugin.endOfDirectory(addon_handle)
    
def reset_addon():
    try:
        if os.path.exists(PICKLE_FILE):
            os.remove(PICKLE_FILE)
        if os.path.exists(CHROME_USER_DATA_PATH):
            shutil.rmtree(CHROME_USER_DATA_PATH)
    except:
        pass        
    
    xbmcplugin.endOfDirectory(addon_handle)
    
while (username == "" or password == ""):
    addon.openSettings()

if mode is None:
    init()
        
elif mode[0] == 'profile': 
    profile_selection()

elif mode[0] == 'category':
    category_selection()

elif mode[0] == 'play':
    play()
    
elif mode[0] == 'deleteCache':
    delete_cache()
    
elif mode[0] == 'resetAddon':
    reset_addon()