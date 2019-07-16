import time
import os
import csv
import io

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#Function for loading as much video as possible with infinite loading
def infiniteLoad(driver, wait_time):
    #getting current scroll height
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        #wait until new info loads
        time.sleep(wait_time)
        #check current height
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        #if the same as the last one break the loop
        if new_height == last_height:
            break
        last_height = new_height


def main():
    options = webdriver.ChromeOptions()

    #getting local appdata google chrome folder
    appdata_fold = os.getenv('APPDATA')
    appdata_fold = appdata_fold.replace('Roaming','Local')
    appdata_fold += '\\Google\\Chrome\\User Data'

    #adding user chrome profile so we can login to youtube without login and password
    options.add_argument('user-data-dir=' + appdata_fold) #if you just want trending then delete/comment this line
    options.add_argument("--headless")
    options.add_argument("log-level=3")

    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://www.youtube.com")

    element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.ID, "video-title")))

    #loading as much video as possible
    print('infinite loading')
    infiniteLoad(driver, 2)

    #sometimes youtube takes time to once again load titles usually takes about ~1 second
    time.sleep(2)

    video_links = []

    #scraping video links
    print("getting links")
    video_list = driver.find_elements_by_xpath("//a[@id='video-title']")
    for video in video_list:
        video_links.append(video.get_attribute("href"))

    #reseting browser with default profile so user's watch history and recommendation doesn't change after loading all of the videos
    driver.quit()
    #to mute youtube videos
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("log-level=3")
    driver = webdriver.Chrome(chrome_options = chrome_options)
    tags = []
    wait = WebDriverWait(driver,10)
    #scraping video tags
    print("getting tags")
    for link in video_links:
        skip = False
        driver.get(link)
        try:     
            script = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="player-wrap"]/script[2]')))
        except:
            skip = True
            
        if skip:
            continue
        script_content = script.get_attribute('innerHTML')
        #extracting tags
        script_list = script_content.split('\\"keywords\\":')
        #some of the videos don't have tags
        if len(script_list) != 2:
            continue
        script_list2 = script_list[1].split('\\"channelId\\":')
        tags_text = script_list2[0]
        tags_text = tags_text.replace('[','')
        tags_text = tags_text.replace(']','')
        tags_text = tags_text.replace('\\','')
        tags_local_list = tags_text.split('",')
        temp_arr = []
        for x in tags_local_list:
            tags.append(x.replace('"',''))


    driver.quit()
    #writing csv
    print("writing output to csv")
    with io.open('output.csv','w',encoding='utf8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tags)

    csvfile.close()

    print("done")


if __name__ == '__main__':
    main()