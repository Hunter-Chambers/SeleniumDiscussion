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
def wait_until_by_xpath(element_to_search_from, condition, locator):
    return WebDriverWait(element_to_search_from, timeout=30)\
        .until(condition((By.XPATH, locator)))
# end wait_until_by_xpath

def parse_song_information_from_table(table_element):
    table_header_row_locator = "./thead/tr"
    title_col_header_locator = "./th[.='Title']"
    table_header_elements_locator = "./th"

    table_header_row = wait_until_by_xpath(table_element,
                                           EC.visibility_of_element_located,
                                           table_header_row_locator)
    title_col_header = wait_until_by_xpath(table_header_row,
                                           EC.visibility_of_element_located,
                                           title_col_header_locator)
    song_title_col_index = wait_until_by_xpath(table_header_row,
                                               EC.visibility_of_all_elements_located,
                                               table_header_elements_locator)\
        .index(title_col_header) + 1

    song_rows_locator = "./tbody/tr"
    song_rows = wait_until_by_xpath(table_element,
                                    EC.visibility_of_all_elements_located,
                                    song_rows_locator)

    song_title_locator = f"./td[{song_title_col_index}]"
    song_artist_locator = f"./td[{song_title_col_index + 1}]"

    remove_symbols_regex = r'[^\w,()\'\.&\[\]\- ]|\[.*\]'

    for song_data in song_rows:
        song_title = wait_until_by_xpath(song_data,
                                         EC.visibility_of_element_located,
                                         song_title_locator)\
            .get_attribute("innerText")
        song_artist = wait_until_by_xpath(song_data,
                                          EC.visibility_of_element_located,
                                          song_artist_locator)\
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

        music_tables_locator = "//table[descendant::th[.='Recording date']]"
        music_tables = wait_until_by_xpath(driver,
                                           EC.visibility_of_all_elements_located,
                                           music_tables_locator)

        for table in music_tables:
            parse_song_information_from_table(table)
        # end for

        driver.get(YOUTUBE)

        search_box_locator = "//input[@id='search']"

        for song_title, song_artist in SONGS.items():
            search_box = wait_until_by_xpath(driver,
                                             EC.visibility_of_element_located,
                                             search_box_locator)

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
