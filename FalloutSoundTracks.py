#!/usr/bin/env python


#######################################################################
# IMPORTS
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


#######################################################################
# GLOBAL VARIABLES
FALLOUT_MUSIC_WIKI = "https://en.wikipedia.org/wiki/Music_of_the_Fallout_series"
YOUTUBE = "https://www.youtube.com/"

SONGS = {}
SONG_URLS = []


#######################################################################
# METHODS
def parse_song_information_from_table(table_element):
    table_header_row = WebDriverWait(table_element, timeout=30)\
        .until(EC.visibility_of_element_located((By.XPATH, "./thead/tr")))
    title_column_header = WebDriverWait(table_header_row, timeout=30)\
        .until(EC.visibility_of_element_located((By.XPATH, "./th[.='Title']")))
    song_title_column_index = WebDriverWait(table_header_row, timeout=30)\
        .until(EC.visibility_of_all_elements_located((By.XPATH, "./th")))\
        .index(title_column_header) + 1

    remove_symbols_regex = r'[^\w,()\'\.&\[\]\- ]|\[.*\]'
    song_rows = WebDriverWait(table_element, timeout=30)\
        .until(EC.visibility_of_all_elements_located((By.XPATH, "./tbody/tr")))
    for song_data in song_rows:
        song_title = WebDriverWait(song_data, timeout=30)\
            .until(EC.visibility_of_element_located((By.XPATH, f"./td[{song_title_column_index}]")))\
            .get_attribute("innerText")\
            .replace("\"", "")
        song_artist = WebDriverWait(song_data, timeout=30)\
            .until(EC.visibility_of_element_located((By.XPATH, f"./td[{song_title_column_index + 1}]")))\
            .get_attribute("innerText")

        song_title = re.sub(remove_symbols_regex, "", song_title)
        song_artist = re.sub(remove_symbols_regex, "", song_artist)

        SONGS[song_title] = song_artist
    # end for
# end parse_song_information_from_table


#######################################################################
# CODE ENTRY
if (__name__ == "__main__"):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(FALLOUT_MUSIC_WIKI)

        music_tables = WebDriverWait(driver, timeout=30)\
            .until(EC.visibility_of_all_elements_located((By.XPATH, "//table[descendant::th[.='Recording date']]")))
        for table in music_tables:
            parse_song_information_from_table(table)
        # end for

        driver.get(YOUTUBE)

        for song_title, song_artist in SONGS.items():
            search_box = WebDriverWait(driver, timeout=30)\
                .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='search']")))
            search_box.clear()
            search_box.send_keys(f"{song_title} by {song_artist}")
            search_box.send_keys(Keys.RETURN)

            WebDriverWait(driver, timeout=30)\
                .until(EC.url_contains(YOUTUBE + "results"))

            searching_for_video = True
            while (searching_for_video):
                try:
                    WebDriverWait(driver, timeout=1)\
                        .until(EC.url_contains(YOUTUBE + "watch"))
                    searching_for_video = False
                except TimeoutException:
                    continue
                # end try/except
            # end while
            SONG_URLS.append(driver.current_url)
        # end for

        for url in SONG_URLS:
            print(url)
        # end for
    except Exception as e:
        print(f"Error encountered:\n{e}")
    finally:
        print("Quitting driver...")
        driver.quit()
    # end try/except
# end entry point if