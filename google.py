from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
import posixpath

class Google:
    def __init__(self, search_query, limit):
        self.search_query = search_query
        self.limit = limit
        self.image_urls = set()
        self.total_downloaded = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

    def get_chrome_driver(self):

        print("Finding/Installing Chrome Driver")

        service = Service(executable_path=ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, chrome_options=options)

        return driver

    def scroll_to_bottom(self, driver, FOOTER):
        while FOOTER.is_displayed() == False:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def download(self):
        if os.path.exists("../images") == False:
            os.makedirs("../images")

        for url in self.image_urls:
            print("Downloading Image From: " + url)
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                self.total_downloaded += 1
                path = parse.urlsplit(url).path
                filename = posixpath.basename(path).split('?')[0]
                file_extension = filename.split(".")[-1]
                if file_extension.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                    file_extension = "jpg"
                
                file_path = "../images/" + "Image_" + str(self.total_downloaded) + "." + file_extension

                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print("File Downloaded!")

            else:
                print("Error while downloading image with status code ", response.status_code)

    def run(self):
        request_url = "https://www.google.com/search?q=" \
                      + parse.quote_plus(self.search_query) \
                      + "&tbm=isch&source=lnms"
        driver = self.get_chrome_driver()

        print("Searching images for '" + self.search_query + "'")

        driver.get(request_url)

        time.sleep(2)
        HTML_BODY = driver.find_elements(By.TAG_NAME,"body")[0]
        FOOTER = driver.find_elements(By.CLASS_NAME, "yQ0wwc")[0]
        LOAD_MORE = driver.find_elements(By.CLASS_NAME, "mye4qd")[0]

        while True:
            self.scroll_to_bottom(driver, FOOTER)
            if LOAD_MORE.is_displayed() == True:
                LOAD_MORE.click()
                self.scroll_to_bottom(driver, FOOTER)
            
            time.sleep(2)            
            IMAGE_ELEMENTS = HTML_BODY.find_elements(By.CLASS_NAME, "Q4LuWd")
            action = ActionChains(driver)
            for IMAGE in IMAGE_ELEMENTS:
                action.move_to_element(IMAGE).click().perform()
                time.sleep(1.5)

                FULL_IMAGES = driver.find_elements(By.CLASS_NAME, "n3VNCb")
                for img in FULL_IMAGES:
                    source = img.get_attribute("src")
                    if source in self.image_urls:
                        continue 
                    if "https" in source:
                        self.image_urls.add(source)
                        print("Found " + str(len(self.image_urls)) + " image(s)")
                    if len(self.image_urls) == self.limit:
                        break
                
                if len(self.image_urls) == self.limit:
                    break

            print("Total images found: ", len(self.image_urls))
            break

        driver.quit() 

        self.download()
