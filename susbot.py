import crewmate #username/password goes in crewmate.py
import requests
import keyboard
import socketio
import threading
import math
import random
import time
import urllib.request
import json
import copy
import PIL
import numpy as np
import itertools
from itertools import cycle
from numpy import sqrt 
from PIL import Image, ImageGrab
from ast import literal_eval as make_tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#driver = webdriver.Firefox() #either use Firefox or Chrome (comment the other out) *Firefox requires geckodriver.exe
driver = webdriver.Chrome() #either use Firefox or Chrome (comment the other out) *chrome requires Chromedriver.exe

sio = socketio.Client()

#OPTIONS:
reddit = "yes" #yes/no... no = you must manually login to pixelplace and then press F9 to connect
board = 7 #map number

#BOT SPEED SETTINGS:
slow_speed = 0.04 #seconds
default_speed = 0.02 #seconds
max_speed = 0.016  #seconds (be careful faster than this -seriously- you can get autobanned for going too fast)

#PAINT RGB VALUES
paintz = ( #here is our list of pixel place colors
        (255,255,255), #the order of them also is the order
        (196,196,196), #of them on pixelplace which makes
        (136,136,136), #referencing them later a breeze
        (85,85,85),    #<<< this one is " paintz[3] " for example
        (34,34,34),    #<<< and this: " paintz.index((34,34,34)) "
        (0,0,0),       #        will equal " 4 " ^^^^^^
        (0,102,0),     #you will need to use both ways to check rgb values
        (34,177,76),   #and send correct color index to pixelplace server
        (2,190,1),     #(if you want to make your own functions that use colors)
        (81,225,25),
        (148,224,68),
        (251,255,91),
        (229,217,0),
        (230,190,12),
        (229,149,0),
        (160,106,66),
        (153,83,13),
        (99,60,31),
        (107,0,0),
        (159,0,0),
        (229,0,0),
        (255,57,4),
        (187,79,0),
        (255,117,95),
        (255,196,159),
        (255,223,204),
        (255,167,209),
        (207,110,228),
        (236,8,236),
        (130,0,128),
        (81,0,255),
        (2,7,99),
        (0,0,234),
        (4,75,255),
        (101,131,207),
        (54,186,255),
        (0,131,199),
        (0,211,221),
        (69,255,200)
        )
#some list of colors for the tree (trunks and leaves) function later:
leaves = [paintz.index(k) for k in paintz if paintz.index(k) in range(6,10+1)]
leaves_cycle = cycle(leaves)
trunks = [paintz.index(k) for k in paintz if paintz.index(k) in range(15,17+1)] + [22]
trunks_cycle = cycle(trunks)

def cy_cols(a): #this is color shifter for the 'tv' to imitate a channel
    if a in range(0,39):
        if random.random() > .7: #adjust the decimal number to adjust 'tv' reception
            a += 1
        else:
            a -= 1 #which results it in either moving a  pixel forward or backwards in the color spectrum
    if a > 38:
        a = 0
    elif a < 0:
        a = 38   
    return a #"return" "a" means that you can say the function itself is equal to something, for example "variable = cy_cols(1)" has a chance to equal 0 or 2

class Sus_Bot(): #---------Sus_Bot main class-----------
    def __init__ (self, username, password): #lets setup the __init__ and load some future needed variables and fully load the bot:
        self.z = 1 #that's right, it equals one... for now...
        self.txty, self.bxby = None, None #and these equal None... for now...
        self.x, self.y = 0, 0 #I think you get the picture now.
        self.colorfilter = [None, None, None, None, None, None, None, None, None]
        self.logos = True
        self.get_7()#map
        self.manualmsg = False
        self.ate_cookies = False
        if reddit == "yes":
            self.login()#login       
            self.auth_data()#cookies                
            self.visibility_state() #this checks the current tab you are on, and correctly sets the xpath stuff
        self.hotkeys()#activate keybinds
        self.connection()
            
    #hotkey binds:
    def hotkeys(self):
        keyboard.on_press(self.onkeypress)#1-9 buttons equip currently selected colors
        keyboard.add_hotkey('shift+y', lambda: self.zone('top left')) #mark top left corner of zone to bot
        keyboard.add_hotkey('shift+u', lambda: self.zone('bottom right')) #mark bottom right corner of zone to bot
        keyboard.add_hotkey('shift+/', lambda: self.restore_area()) #restore zone from backup
        keyboard.add_hotkey('shift+c', lambda: self.copy_img()) #copy zone
        keyboard.add_hotkey('shift+v', lambda: self.paste_img('center')) #paste zone
        keyboard.add_hotkey('shift+b', lambda: self.paste_img('corner')) #paste zone
        keyboard.add_hotkey('shift+x', lambda: self.toggle_logos()) #toggle guild war logos on/off
        keyboard.add_hotkey("shift+'", lambda: self.rectangle_scatter('not alt')) #paint on equipped colors in zone
        keyboard.add_hotkey("shift+;", lambda: self.rectangle_scatter('alt')) #paint 'not' on equipped colors in zone
        keyboard.add_hotkey("shift+r", lambda: self.lgbt()) #paint on equipped colors in zone
        keyboard.add_hotkey("shift+q", lambda: self.tv_screen('on')) #paint on equipped colors in zone
        keyboard.add_hotkey("shift+e", lambda: self.amogus()) #sus
        keyboard.add_hotkey("shift+z", lambda: self.tree()) #sus
        print('Hotkeys on.')
        
    def connection(self): #maintain socket connection and update pixel cache
            sio.connect('https://pixelplace.io', transports=['websocket'])

            @sio.event
            def connect(): #"Hello there."
                sio.emit("init",{"authKey":f"{self.authkey}","authToken":f"{self.authtoken}","authId":f"{self.authid}","boardId":board})
                threading.Timer(15, connect).start()
            
            @sio.on("p")
            def update_pixels(p: tuple): #To the cache cave!
                for i in p:
                    self.cache[i[0], i[1]] = paintz[i[2]]
            
    def tree(self): #this will draw a randomly colored tree
        try:
            self.get_coordinate()
            x, y = self.x, self.y       
            trunk=next(trunks_cycle)
            for a in range(4):
                sio.emit("p",[x,y-a,trunk,1])
                time.sleep(max_speed)            
            leaf=next(leaves_cycle)
            y -= a
            for b in range(3):
                sio.emit("p",[x+b-1,y,leaf,1])
                time.sleep(max_speed)
            y -= 1
            for c in range(3):
                sio.emit("p",[x+c-1,y,leaf,1])
                time.sleep(max_speed)
            y -= 1 
            sio.emit("p",[x,y,leaf,1])        
            time.sleep(max_speed)
        except:
            pass
            
    def amogus(self): #lil sussy baka, or crewmate, who is to tell?
        try:
            self.get_coordinate()
            X, Y = self.x, self.y
            self.z = -self.z
            for n in range(2):#visor
                sio.emit("p",[X+(n*self.z),Y,38,1])
                time.sleep(default_speed)                
            x, y = X + self.z, Y + 2            
            body=[(x,y),(x,y-1),(x-self.z,y-1),(x-self.z-self.z,y),(x-self.z-self.z,y-1),(x-self.z-self.z-self.z,y-1),
                  (x-self.z-self.z-self.z,y-2),(x-self.z-self.z,y-2),(x-self.z-self.z,y-3),(x-self.z,y-3),(x,y-3)]            
            c = random.randrange(0,37)            
            for n in body:#body
                sio.emit("p",[n[0],n[1],c,1])            
                time.sleep(default_speed)                
        except:
            pass
        
    def tv_screen(self, on): #"Don't watch too much TV or you will rot your brain." - Mom, probably
        if on == 'on':
            p = 0
            try:
                print('Activating TV. Press F8 to stop.')
                while True:
                    self.work_order=()
                    self.imagecrop = self.image.crop((self.txty[0], self.txty[1], self.bxby[0], self.bxby[1]))
                    self.cachecrop = self.imagecrop.load() 
                    #iterate through and emit qualifed pixels:
                    for X in range(self.imagecrop.size[0]): #horizontal   
                        for Y in range(self.imagecrop.size[1]): #vertical
                            if self.cachecrop[X, Y] != (204,204,204) and self.cachecrop[X, Y] not in self.colorfilter:
                                self.work_order += ([X,Y, cy_cols(paintz.index(self.cachecrop[X, Y]))],)
                    self.work_order = self.randtup(self.work_order, 2)#re-order by index 2  
                    for job in self.work_order:                
                        sio.emit("p",[job[0]+self.txty[0],job[1]+self.txty[1],job[2],1])
                        time.sleep(default_speed)#following pixelplace speed limit
                        p += 1
                        if keyboard.is_pressed("f8"):
                            print('Deactivating TV.')
                            print(f'{p} pixels farmed.')
                            return
            except:
                pass
        
    def copy_img(self):
        try:
            self.work_order=()
            print(f'Copying: {self.txty} to {self.bxby}')      
            self.imagecrop = self.image.crop((self.txty[0], self.txty[1], self.bxby[0], self.bxby[1]))
            self.cachecrop = self.imagecrop.load()        
            #iterate through and emit qualifed pixels:
            for X in range(self.imagecrop.size[0]): #horizontal   
                for Y in range(self.imagecrop.size[1]): #vertical
                    if self.cachecrop[X, Y] != (204,204,204) and self.cachecrop[X, Y] not in self.colorfilter:
                        self.work_order += ([X,Y, paintz.index(self.cachecrop[X, Y])],)                        
            self.work_order = self.randtup(self.work_order, 2)
            print('Copy complete.')
        except:
            pass
    
    def paste_img(self, loc):
        try:
            self.getcurcolor()
            self.get_coordinate()
            if loc == 'center':
                imagecrop = self.image.crop((int(self.x -(self.imagecrop.size[0]/2)), int(self.y-(self.imagecrop.size[1]/2)), int(self.x+(self.imagecrop.size[0]/2)), int(self.y+(self.imagecrop.size[1]/2))))
            elif loc == 'corner':
                imagecrop = self.image.crop((self.x , self.y, self.x+self.imagecrop.size[0], self.y+self.imagecrop.size[1]))
            cachecrop = imagecrop.load() 
            print(f'Starting print job at: {self.x, self.y}')
            for job in self.work_order:           
                if keyboard.is_pressed('f8'): #(press 'F8' to stop the function)
                    print(f'Printing at {self.x, self.y} cancelled.')
                    time.sleep(.5) #short nap to compensate for depress delay
                    return #aborted
                if cachecrop[job[0],job[1]] in tuple([paintz[job[2]]] + [(204,204,204)] + self.colorfilter):
                    pass
                else:
                    if loc == 'center':
                        sio.emit("p",[int(job[0]+self.x-imagecrop.size[0]/2),int(job[1]+self.y-imagecrop.size[1]/2),job[2],1])
                        time.sleep(default_speed)#following pixelplace speed limit
                    elif loc == 'corner':
                        sio.emit("p",[job[0]+self.x,job[1]+self.y,job[2],1])
                        time.sleep(default_speed)#following pixelplace speed limit
            print('Done.')
        except:
            pass

    def rectangle_scatter(self, alt): #two different modes, paints on filter colors or paints non-filter colors
        try:
            self.getcurcolor()
            self.work_order=()    
            self.imagecrop = self.image.crop((self.txty[0], self.txty[1], self.bxby[0], self.bxby[1]))
            self.cachecrop = self.imagecrop.load()            
            for X in range(self.bxby[0] - self.txty[0]): #horizontal   
                for Y in range(self.bxby[1] - self.txty[1]): #vertical
                    if self.cachecrop[X, Y] in self.colorfilter and alt == 'alt':                   
                        self.work_order += ([X,Y, paintz.index(self.curcol[0])],)
                    elif self.cachecrop[X, Y] not in self.colorfilter and alt != 'alt':
                        self.work_order += ([X,Y, paintz.index(self.curcol[0])],)
            jobs = list(self.work_order)
            random.shuffle(jobs)
            self.work_order = tuple(jobs)            
            for job in self.work_order:
                if keyboard.is_pressed('f8'): #(press 'F8' to stop the function)
                    print(f'Printing at {self.x, self.y} cancelled.')
                    time.sleep(.5) #short nap to compensate for depress delay
                    return #aborted
                if paintz[job[2]] == self.cachecrop[job[0],job[1]]:
                    pass
                elif self.cachecrop[job[0]-1,job[1]-1] == (204,204,204):
                    pass
                else:
                    sio.emit("p",[job[0]+self.txty[0],job[1]+self.txty[1],job[2],1])
                    time.sleep(default_speed)#following pixelplace speed limit
            print('Done.')
        except:
            pass

    def lgbt(self): #draws rng striped flags in zone
        try:
            while True:
                a,b = random.randint(self.txty[0], self.bxby[0]), random.randint(self.txty[1]-10, self.bxby[1]-7)
                for A in range(7):
                    color = random.choice([x for x in range(38)])
                    for B in range(11):
                        if keyboard.is_pressed('f8'): #(press 'F8' to stop the function)
                            print(f'Printing at {self.x, self.y} cancelled.')
                            time.sleep(.5) #short nap to compensate for depress delay
                            return #aborted
                        sio.emit("p",[a+B,b+A,color,1])
                        time.sleep(default_speed)#following pixelplace speed limit
        except:
            pass
                    
    def randtup(self, w_order, ind): #requires tuple as input + 'ind', orders it by index x[ind]
        try:
            w_order = list(w_order)
            random.shuffle(w_order)
            w_order.sort(key = lambda x: x[ind]) #ind = index, usually either 0, 1, or 2 for this bot
            w_order = tuple(w_order)
            return w_order
        except:
            pass
    
    def restore_area(self): #restores an area, change 7place.png to a custom image as the same size, same color data as the map you are playing on
        try:
            self.work_order=()
            #map you want to use to restore to:        
            restore = PIL.Image.open('7place.png').convert('RGB')
            #get a crop of the area you are restoring:
            restorecrop = restore.crop((self.txty[0], self.txty[1], self.bxby[0], self.bxby[1]))
            imagecrop = self.image.crop((self.txty[0], self.txty[1], self.bxby[0], self.bxby[1]))        
            restcache = restorecrop.load()
            cachecrop = imagecrop.load()        
            #iterate through and emit qualifed pixels:
            print('Restoration preperation... please wait...')
            for X in range(imagecrop.size[0]): #horizontal
                for Y in range(imagecrop.size[1]): #vertical
                    if restcache[X, Y] not in tuple((204,204,204) + cachecrop[X, Y]):
                        self.work_order += ([X,Y, paintz.index(restcache[X, Y]), 1],)
                    if keyboard.is_pressed('f8'): #press 'F8' to stop the function
                        print('Aborted during restoration preperation.')
                        time.sleep(.5) #short nap to compensate for depress delay
                        return #aborted                        
            self.work_order  = self.randtup(self.work_order, 2) #order by color, see function for details            
            print(f'Restoring: {self.txty} to {self.bxby}')
            for job in self.work_order:
                if keyboard.is_pressed('f8'): #press 'F8' to stop the function
                    print('Aborted restoration.')
                    time.sleep(.5) #short nap to compensate for depress delay
                    return #aborted
                if cachecrop[job[0],job[1]] in tuple([paintz[job[2]]] + [(204,204,204)] + self.colorfilter):
                    pass
                else:
                    sio.emit("p",[job[0]+self.txty[0],job[1]+self.txty[1], job[2], 1])
                    time.sleep(default_speed)#following pixelplace speed limit 
            print('Finished restoration.')
        except:
            pass
        
    def get_coordinate(self):#check the coordinate of where your cursor is on the selenium pixelplace site
        try:
            self.x, self.y = make_tuple(driver.find_element(By.XPATH,'/html/body/div[3]/div[4]').text)
        except:
             pass

    def zone(self, hotkey): #zone constructor
        try:
            self.get_coordinate()
            if hotkey == 'top left': #top left
                self.txty = self.x, self.y
                print (f'Top-left mark created at: {self.txty}')
                try:
                    if self.bxby[0] > self.txty[0] and self.bxby[1] > self.txty[1]:
                        print ('Zone ready.')
                except:
                    pass
            if hotkey == 'bottom right': #bottom right
                self.bxby = self.x + 1, self.y + 1
                print (f'Bottom-right mark created at: {self.bxby}')
                try:
                    if self.bxby[0] > self.txty[0] and self.bxby[1] > self.txty[1]:
                        print ('Zone commands ready.')
                except:
                    pass
        except:
            pass
        
    def onkeypress(self, event): #whatever 1-9 key you press will allow you to equip a color for filter
        if event.name == '1':
            self.getcurcolorhotkey(1)
        elif event.name == '2':
            self.getcurcolorhotkey(2)
        elif event.name == '3':
            self.getcurcolorhotkey(3)
        elif event.name == '4':
            self.getcurcolorhotkey(4)
        elif event.name == '5':
            self.getcurcolorhotkey(5)
        elif event.name == '6':
            self.getcurcolorhotkey(6)
        elif event.name == '7':
            self.getcurcolorhotkey(7)
        elif event.name == '8':
            self.getcurcolorhotkey(8)
        elif event.name == '9':
            self.getcurcolorhotkey(9)
        elif event.name == '0':
            self.removefilters()
            
    def getcurcolor(self): #gets the currently equipped color as a tuple
        try:
            self.visibility_state()
            a = self.curcol.find('(')
            b = self.curcol.find(')');b+=1
            self.curcol = self.curcol[a:b]
            self.curcol = [make_tuple(self.curcol)]
        except:
            pass
        
    def getcurcolorhotkey(self, col): #equips color to 1-9 slots
        try:
            self.visibility_state()
            a = self.curcol.find('(')
            b = self.curcol.find(')');b+=1
            curcol = self.curcol[a:b]
            self.curcol = [make_tuple(curcol)]
            self.colorfilter[col-1] = self.curcol[0]
            print(f'Equipped {self.curcol[0]} to slot {col}')
            time.sleep(1)
            return
        except:
            pass
    
    def removefilters(self): #removes equipped colors on the 1-9 slots
        self.colorfilter[0:] = None, None, None, None, None, None, None, None, None
        print("Filters dequipped.")
        time.sleep(1)
        
    def visibility_state(self): #ensures the current tab is correctly loaded for xpath css code stuff
        try:
            vis = driver.execute_script("return document.visibilityState") == "visible"
        except:
            driver.switch_to.window(driver.window_handles[0])
            vis = driver.execute_script("return document.visibilityState") == "visible"
        if vis == False:
            p = driver.current_window_handle
            chwd = driver.window_handles
            for w in chwd:
                if(w!=p):
                    driver.switch_to.window(w)
            self.curcol = str(driver.find_element(By.XPATH,'/html/body/div[3]/div[2]').get_attribute("style"))
        else:
            self.curcol = str(driver.find_element(By.XPATH,'/html/body/div[3]/div[2]').get_attribute("style"))
            
    def toggle_logos(self): #toggles guild war logos on and off
        self.visibility_state()
        if self.logos == True:
            for lg in range(10):
                try:
                    driver.execute_script("arguments[0].style.display = 'none';",driver.find_element(By.XPATH,f'//*[@id="areas"]/div[{lg}]'))
                except:
                    pass
            self.logos = False
        else:
            for lg in range(10):
                try:
                    driver.execute_script("arguments[0].style.display = 'block';",driver.find_element(By.XPATH,f'//*[@id="areas"]/div[{lg}]'))
                except:
                    pass
            self.logos = True
        time.sleep(.5)
        
    def get_7(self):#gets the latest download of map
        urllib.request.urlretrieve(f"https://pixelplace.io/canvas/{board}.png", f"{board}.png")
        self.image = PIL.Image.open(f'{board}.png').convert('RGB')
        self.cache = self.image.load() #individual pixels with = self.cache[x, y]
        
    def manual(self): #manual login stuff
        driver.get(f"https://pixelplace.io/{board}")
        print("After you login in manually, press F9.")

    def manualF9(self): #manual login stuff
        self.visibility_state()
        self.auth_data()
        self.ate_cookies = True
        keyboard.remove_hotkey('f9')
        self.connection()        
        
    def login(self): #logins to pixelplace through reddit
        driver.get("https://pixelplace.io/api/sso.php?type=2&action=login")
        driver.find_element(By.ID,'loginUsername').send_keys(crewmate.username)
        driver.find_element(By.ID,'loginPassword').send_keys(crewmate.password)
        driver.find_elements(By.XPATH,'/html/body/div/main/div[1]/div/div[2]/form/fieldset')[4].click()
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div/div[2]/form/div/input'))).click()
        try:
            WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH,'/html/body/div[5]/div[2]/a/img'))).click()
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[8]/a[2]/div[3]/button[2]'))).click()
        except:
            pass
        print('Logged in.')
        return

    def auth_data(self): #gets your cookies for pixelplace
        self.authkey = driver.get_cookie("authKey").get('value')
        self.authtoken = driver.get_cookie("authToken").get('value')
        self.authid = driver.get_cookie("authId").get('value')
        print('got cookies! yum!')
        self.ate_cookies = True
    
goto = Sus_Bot(crewmate.username, crewmate.password) #start an instance of the Sus_Bot class as 'goto'
