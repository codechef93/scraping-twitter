import sys
import time
import traceback
import getpass
import tkinter as tk
import xlsxwriter
from PIL import Image, ImageChops
from io import BytesIO
import lxml.html
from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains
import os
import re

import argparse
import datetime

try:
    os.mkdir('./screenshots/')
except:
    pass
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--long', action='store_true', help="Enable clicking on links")
parser.add_argument('-m', '--month', action='store_true', help="Increase search time period from 10 days to 1 month")
args = parser.parse_args()

if args.long:
    flag = 1
else:
    flag = 0

username = input("Please enter username: ")
password = getpass.getpass('Please enter password: ') 
profile_path = input("Please enter the name of the file with profiles: ") or "inputs.txt"
# profile_path = input("Please enter profile link here: ")

f = open(profile_path,'r')
lines = f.readlines()
f.close()
first_time = 1

options = webdriver.ChromeOptions()
options.add_argument('--disable-notifications')
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--no-sandbox')
options.add_argument('--start-maximized')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--log-level=3")
options.headless = True
browser = webdriver.Chrome(executable_path=r"E:\Web\chromedriver.exe", options=options)
browser.set_window_size(1920, 1080)    
url = "https://twitter.com/login"
#url = 'https://whatismyipaddress.com/proxy-check'
browser.get(url)     

login_username = browser.find_element_by_xpath("//input[@name='session[username_or_email]']")
login_password = browser.find_element_by_xpath("//input[@name='session[password]']")

login_username.send_keys(username)
login_password.send_keys(password)
login_password.submit()
time.sleep(2)

if browser.current_url == "https://twitter.com/login/error?username_or_email=dsf&redirect_after_login=%2F":
    print("Incorrect sign-in details")
    exit()

#Loop through every account in link
for line in lines:
    url_list = []
    print(f"Scraping - {line}")
    handle = line.split('/')[3]
    match = re.search(r"([\w]+)", handle).group()
    handle = match
    tab = ''    

    try:
        os.mkdir(f"./screenshots/{handle}/")
    except:
        pass

    #Create a folder for the screenshots
    if len(line.split('/')) > 4:
        tab = line.split('/')[4].rstrip()
        
        try:
            tab = re.search(r"([\w]+)", tab).group()            
            os.mkdir("./screenshots/"+handle+'/'+tab)
        except:
            pass        
        

    join_month = "July"
    join_year = 2020
    now = datetime.date.today()            

    browser.get(line)
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="primaryColumn"]')))

    element = browser.find_element_by_xpath('//div[@data-testid="primaryColumn"]')
    location = element.location
    size = element.size
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()         
    current_height = 0
    q = 0
    counter = 1
    count = 0
    new_links = []

    last_height = browser.execute_script("return document.body.scrollHeight")

    info = browser.find_elements_by_xpath('//span[@class="css-901oao css-16my406 r-1re7ezh r-4qtqp9 r-1qd0xha r-ad9z0x r-zso239 r-bcqeeo r-qvutc0"]')
    if info:
        info = info[-1].text.split()
        join_month = info[1]
        join_year = int(info[2])
        print(join_month,join_year)

    for year in range(join_year, now.year+1):
        try:
            os.mkdir(f'./screenshots/{handle}/{year}/')
        except:
            pass

        if year==now.year:
            month_limit = now.month+1
        else:
            month_limit = 13        

        for month in range(1,month_limit):
            datetime_object = datetime.datetime.strptime(join_month, "%B")
            if year==join_year and month<int(datetime_object.month):
                continue
            
            try:
                os.mkdir(f'./screenshots/{handle}/{year}/{month}')
            except:
                pass

            if month in [1,3,5,7,10,12]:
                end_day = 31
            elif month in [4,6,9,11]:
                end_day = 30
            elif month==2 and (year%4 == 0):
                end_day = 29
            else:
                end_day = 28
            
            if args.month:
                url_list = []
                start_date = f"{year}-{month}-01"
                if month != 12:    
                    end_date = f"{year}-{month+1}-01"
                else:
                    end_date = f"{year}-{month}-31"

                search_url = f'https://twitter.com/search?q=(from%3A{handle})%20OR%20(to%3A{handle})%20OR%20(%40{handle})%20since%3A{start_date}%20until%3A{end_date}%20include%3Anativeretweets%20include%3Aretweets&src=typed_query'

                browser.get(search_url)
                #time.sleep(2)

                wait = WebDriverWait(browser, 10)
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Search timeline"]')))
                element = browser.find_element_by_xpath('//div[@aria-label="Timeline: Search timeline"]')
                location = element.location
                size = element.size
                root = tk.Tk()

                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()         
                #current_height = location['y']-90
                #scroll_height = 99999999
                #rep_count = 0
                current_height = 0
                q = 0
                counter = 1
                count = 0
                new_links = []
                last_height = browser.execute_script("return document.body.scrollHeight")

                while True:
                    see_more = element.find_elements_by_xpath("//a[contains(@href, '/i/status')]")
                    if see_more and flag:
                        for bt in see_more:
                            try:
                                link = bt.get_attribute("href")
                                if link in new_links:
                                    pass
                                else:
                                    new_links.append(link) 
                            except:
                                pass

                    browser.save_screenshot(f"./screenshots/{handle}/{year}/{month}/{handle}_"+str(counter)+".png")
                    ## Calculate new scroll height and compare with last scroll height.
                    imshot = Image.open(f"./screenshots/{handle}/{year}/{month}/{handle}_"+str(counter)+".png") # uses PIL library to open image in memory
                    imshot = imshot.crop((location['x'], location['y'], location['x']+size['width'], screen_height-80)) # defines crop points
                    imshot.save(f"./screenshots/{handle}/{year}/{month}/{handle}_"+str(counter)+".png")
                    #current_height = current_height + (0.553 * screen_height)
                    counter  = counter + 1              
                    # Scroll down to the bottom.
                    browser.execute_script("window.scrollTo(0, arguments[0]);", current_height + screen_height - 300)
                    time.sleep(2)
                    browser.execute_script("window.blur();")
                    current_height = current_height + screen_height - 300        

                    if counter > 3:
                        imshot1 = Image.open(f"./screenshots/{handle}/{year}/{month}/{handle}_"+str(counter-1)+".png").convert("RGB")
                        imshot1 = imshot1.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                        imshot1.save(f"./screenshots/{handle}/{year}/{month}/{handle}_"+"dummy1.png")     
                        imshot2 = Image.open(f"./screenshots/{handle}/{year}/{month}/{handle}_"+str(counter-2)+".png").convert("RGB")
                        imshot2 = imshot2.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                        imshot2.save(f"./screenshots/{handle}/{year}/{month}/{handle}_"+"dummy2.png")       

                        diff = ImageChops.difference(imshot1, imshot2)
                        if diff.getbbox():
                            count = 0
                        else:
                            count += 1
                            if count > 5:
                                print("Break")
                                break                      

                    new_height = browser.execute_script("return document.body.scrollHeight")

                    if last_height >= new_height:
                        if count > 5:
                            break
                        else:
                            count+=1
                    else:
                        count = 0
                        
                    last_height = new_height             
                    q+=1
                
                counter = 1
                for link in new_links:

                    try:
                        os.mkdir(f'./screenshots/{handle}/{year}/{month}/additional/')
                    except:
                        pass


                    browser.get(link)
                    #time.sleep(3)

                    wait = WebDriverWait(browser, 10)
                    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Search timeline"]')))
                    element = browser.find_element_by_xpath('//div[contains(@aria-label, "Timeline: Conversation")]')
                    location = element.location
                    size = element.size
                    root = tk.Tk()
                    screen_width = root.winfo_screenwidth()
                    screen_height = root.winfo_screenheight()              

                    current_height = 0
                    q = 0
                    count = 0

                    last_height = browser.execute_script("return document.body.scrollHeight")

                    while True:
                        see_more = browser.find_elements_by_xpath("//div[@class='css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-o7ynqc r-6416eg']")
                        if see_more:
                            for bt in see_more:
                                bt.click()
                                time.sleep(1)
                        time.sleep(1)
                        try:
                            see_more = browser.find_elements_by_xpath("//div[@role='button' and contains(@class,'css-18t94o4 css-1dbjc4n r-1ylenci r-1ny4l3l r-ou255f r-o7ynqc r-6416eg')]")
                            for bt in see_more:
                                bt.click()
                                time.sleep(1)            
                        except:
                            pass

                        browser.save_screenshot(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png")
                        ## Calculate new scroll height and compare with last scroll height.
                        imshot = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png") # uses PIL library to open image in memory
                        imshot = imshot.crop((location['x'], location['y'], location['x']+size['width'], screen_height-80)) # defines crop points
                        imshot.save(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png")
                        #current_height = current_height + (0.553 * screen_height)
                        counter  = counter + 1              
                        # Scroll down to the bottom.
                        browser.execute_script("window.scrollTo(0, arguments[0]);", current_height + screen_height - 300)
                        time.sleep(2)
                        browser.execute_script("window.blur();")
                        current_height = current_height + screen_height - 300        

                        if counter > 3:
                            imshot1 = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter-1)+".png").convert("RGB")
                            imshot1 = imshot1.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                            imshot1.save(f'./screenshots/{handle}/{year}/{month}/additional/'+"dummy1.png")     
                            imshot2 = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter-2)+".png").convert("RGB")
                            imshot2 = imshot2.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                            imshot2.save(f'./screenshots/{handle}/{year}/{month}/additional/'+"dummy2.png")       

                            diff = ImageChops.difference(imshot1, imshot2)
                            if diff.getbbox():
                                count = 0
                            else:
                                count += 1
                                if count > 5:
                                    print("Break")
                                    break                      

                        new_height = browser.execute_script("return document.body.scrollHeight")

                        if last_height >= new_height:
                            if count > 5:
                                break
                            else:
                                count+=1
                        else:
                            count = 0
                            
                        last_height = new_height             
                        q+=1
            else:
                for wk in range(3):
                    url_list = []
                    try:
                        os.mkdir(f'./screenshots/{handle}/{year}/{month}/{wk}/')
                    except:
                        pass                


                    if wk == 2:
                        start_date = f"{year}-{month}-{str(1+(10*wk))}"
                        end_date =  f"{year}-{month}-{end_day}"
                    else:
                        start_date = f"{year}-{month}-{str(1+(10*wk))}"
                        end_date = f"{year}-{month}-{str(11+(10*wk))}"                

                    search_url = f'https://twitter.com/search?q=(from%3A{handle})%20OR%20(to%3A{handle})%20OR%20(%40{handle})%20since%3A{start_date}%20until%3A{end_date}%20include%3Anativeretweets%20include%3Aretweets&src=typed_query'

                    browser.get(search_url)
                    time.sleep(2)

                    element = browser.find_element_by_xpath('//div[@aria-label="Timeline: Search timeline"]')
                    location = element.location
                    size = element.size
                    root = tk.Tk()

                    screen_width = root.winfo_screenwidth()
                    screen_height = root.winfo_screenheight()         
                    #current_height = location['y']-90
                    #scroll_height = 99999999
                    #rep_count = 0
                    current_height = 0
                    q = 0
                    counter = 1
                    count = 0
                    new_links = []
                    last_height = browser.execute_script("return document.body.scrollHeight")

                    while True:
                        see_more = element.find_elements_by_xpath("//a[contains(@href, '/i/status')]")
                        if see_more and flag:
                            for bt in see_more:
                                try:
                                    link = bt.get_attribute("href")
                                    if link in new_links:
                                        pass
                                    else:
                                        new_links.append(link) 
                                except:
                                    pass

                        browser.save_screenshot(f"./screenshots/{handle}/{year}/{month}/{wk}/"+str(counter)+".png")
                        ## Calculate new scroll height and compare with last scroll height.
                        imshot = Image.open(f"./screenshots/{handle}/{year}/{month}/{wk}/"+str(counter)+".png") # uses PIL library to open image in memory
                        imshot = imshot.crop((location['x'], location['y'], location['x']+size['width'], screen_height-80)) # defines crop points
                        imshot.save(f"./screenshots/{handle}/{year}/{month}/{wk}/"+str(counter)+".png")
                        #current_height = current_height + (0.553 * screen_height)
                        counter  = counter + 1              
                        # Scroll down to the bottom.
                        browser.execute_script("window.scrollTo(0, arguments[0]);", current_height + screen_height - 300)
                        time.sleep(2)
                        browser.execute_script("window.blur();")
                        current_height = current_height + screen_height - 300        

                        if counter > 3:
                            imshot1 = Image.open(f"./screenshots/{handle}/{year}/{month}/{wk}/"+str(counter-1)+".png").convert("RGB")
                            imshot1 = imshot1.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                            imshot1.save(f"./screenshots/{handle}/{year}/{month}/{wk}/"+"dummy1.png")     
                            imshot2 = Image.open(f"./screenshots/{handle}/{year}/{month}/{wk}/"+str(counter-2)+".png").convert("RGB")
                            imshot2 = imshot2.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                            imshot2.save(f"./screenshots/{handle}/{year}/{month}/{wk}/"+"dummy2.png")       

                            diff = ImageChops.difference(imshot1, imshot2)
                            if diff.getbbox():
                                count = 0
                            else:
                                count += 1
                                if count > 5:
                                    print("Break")
                                    break                      

                        new_height = browser.execute_script("return document.body.scrollHeight")

                        if last_height >= new_height:
                            if count > 5:
                                break
                            else:
                                count+=1
                        else:
                            count = 0
                            
                        last_height = new_height             
                        q+=1
                    
                    counter = 1
                    for link in new_links:

                        try:
                            os.mkdir(f'./screenshots/{handle}/{year}/{month}/additional/')
                        except:
                            pass


                        browser.get(link)
                        time.sleep(3)

                        element = browser.find_element_by_xpath('//div[contains(@aria-label, "Timeline: Conversation")]')
                        location = element.location
                        size = element.size
                        root = tk.Tk()
                        screen_width = root.winfo_screenwidth()
                        screen_height = root.winfo_screenheight()              

                        current_height = 0
                        q = 0
                        count = 0

                        last_height = browser.execute_script("return document.body.scrollHeight")

                        while True:
                            see_more = browser.find_elements_by_xpath("//div[@class='css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-o7ynqc r-6416eg']")
                            if see_more:
                                for bt in see_more:
                                    bt.click()
                                    time.sleep(1)
                            #time.sleep(1)
                            try:
                                see_more = browser.find_elements_by_xpath("//div[@role='button' and contains(@class,'css-18t94o4 css-1dbjc4n r-1ylenci r-1ny4l3l r-ou255f r-o7ynqc r-6416eg')]")
                                for bt in see_more:
                                    bt.click()
                                    time.sleep(1)            
                            except:
                                pass

                            browser.save_screenshot(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png")
                            ## Calculate new scroll height and compare with last scroll height.
                            imshot = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png") # uses PIL library to open image in memory
                            imshot = imshot.crop((location['x'], location['y'], location['x']+size['width'], screen_height-80)) # defines crop points
                            imshot.save(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter)+".png")
                            #current_height = current_height + (0.553 * screen_height)
                            counter  = counter + 1              
                            # Scroll down to the bottom.
                            browser.execute_script("window.scrollTo(0, arguments[0]);", current_height + screen_height - 300)
                            time.sleep(2)
                            browser.execute_script("window.blur();")
                            current_height = current_height + screen_height - 300        

                            if counter > 3:
                                imshot1 = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter-1)+".png").convert("RGB")
                                imshot1 = imshot1.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                                imshot1.save(f'./screenshots/{handle}/{year}/{month}/additional/'+"dummy1.png")     
                                imshot2 = Image.open(f'./screenshots/{handle}/{year}/{month}/additional/'+str(counter-2)+".png").convert("RGB")
                                imshot2 = imshot2.crop((0, screen_height-80-location['y']-200, size['width'], screen_height-80-location['y']))
                                imshot2.save(f'./screenshots/{handle}/{year}/{month}/additional/'+"dummy2.png")       

                                diff = ImageChops.difference(imshot1, imshot2)
                                if diff.getbbox():
                                    count = 0
                                else:
                                    count += 1
                                    if count > 5:
                                        print("Break")
                                        break                      

                            new_height = browser.execute_script("return document.body.scrollHeight")

                            if last_height >= new_height:
                                if count > 5:
                                    break
                                else:
                                    count+=1
                            else:
                                count = 0
                                
                            last_height = new_height             
                            q+=1                
        
    print("Finished scraping.")

   