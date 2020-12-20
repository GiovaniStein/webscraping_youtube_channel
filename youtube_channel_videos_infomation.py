import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import csv

id_channel = 'id'

main_url = "https://www.youtube.com/channel/" + id_channel + "/videos"

option = Options()
# option.headless = True
option.add_argument("--start-maximized")
option.add_argument("--mute-audio")

driver = webdriver.Chrome('chromedriver.exe', options=option)

driver.get(main_url)

action = ActionChains(driver)

videos_urls = []


def format_date(date):
    months = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'sep', 'out', 'nov', 'dez']
    date_split = date.split("de")

    day = int(date_split[0].strip())
    month = months.index(date_split[1].replace(".", "").strip()) + 1
    year = date_split[2].strip()

    day_formated = ("0" + str(day) if day < 10 else str(day))
    month_formated = ("0" + str(month) if month < 10 else str(month))

    return day_formated + "/" + month_formated + "/" + year


def move_scrool_end_page():
    scrool_pause_time = 1

    last_height = driver.execute_script("return document.getElementById('page-manager').scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.getElementById('page-manager').scrollHeight);")
        time.sleep(scrool_pause_time)
        new_height = driver.execute_script("return document.getElementById('page-manager').scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_links():
    main_div = driver.find_element_by_id("primary")
    div_items = main_div.find_element_by_id("items")
    tags_a = div_items.find_elements_by_tag_name("a")

    for link in tags_a:
        url = link.get_attribute("href") + "||time" + link.text
        if url not in videos_urls and ":" in link.text:
            videos_urls.append(url)


def get_main_informations(video_values):
    main_div = driver.find_element_by_id("info-contents")
    container = main_div.find_element_by_id("container")
    h1_title = container.find_element_by_tag_name("h1")
    video_values["title"] = h1_title.text
    container_info = main_div.find_element_by_id("info").find_element_by_id("info-text")

    count_views = container_info.find_element_by_id("count").text.split(" ")[0]
    date_video = container_info.find_element_by_id("date")
    video_values["count_views"] = count_views
    video_values["post_date"] = format_date(date_video.find_element_by_tag_name("yt-formatted-string").text)

    bar_sentiment = main_div.find_element_by_tag_name("ytd-sentiment-bar-renderer")
    like_or_deslike = bar_sentiment.find_element_by_id("tooltip").get_attribute('innerHTML').strip().split("/")
    video_values["likes"] = like_or_deslike[0]
    video_values["deslikes"] = like_or_deslike[1]

    driver.execute_script("window.scrollTo(0, document.getElementById('page-manager').scrollHeight/3);")
    time.sleep(2)
    comments_container = driver.find_element_by_id("comments")
    video_values["comments_count"] = comments_container.find_element_by_tag_name("h2").text.split(" ")[0]


def run_extract_video_information():
    contains_header = False
    with open('teste_youtube.csv', mode='w', newline='') as csv_file:
        for url in videos_urls:
            url_video = url.split("||time")[0]
            driver.get(url_video)
            time.sleep(1)
            video_values = {"time": url.split("||time")[1]}
            get_main_informations(video_values)
            if not contains_header:
                fieldnames = video_values.keys()
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                contains_header = True
            writer.writerow(video_values)
            print(video_values)


move_scrool_end_page()
get_links()
run_extract_video_information()
driver.quit()
