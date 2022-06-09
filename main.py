from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, InvalidArgumentException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import re
from collections import Counter

import time

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(executable_path=r'C:\Users\galie\Desktop\OGAME\geckodriver.exe', options=options)
driver.maximize_window()  # For maximizing window

littleHelp = ["France", "le", "la", "l", "les", "une", "un", "de", "du", "des", "d", "a", "à", "ou", "est", "et",
              "après",
              "avant", "par", "il", "ils", "elle", "elles", "en", "laquelle", "lequel", "lorsque", "quand", "encore"]
alreadyGuessed = []
alreadyVisited = []
noLuck = ["politique", "cyclisme", "football", "fonction d'onde", "religion", "physique", "science",
          "sentiment", "histoire", "industrie", "animal", "géographie",
          "guerre", "rage", "Nantes", "Munich", "Nankin", "Science-fiction", "Truffe", "Histoire de l'Australie",
          "Émeu d'Australie", "Magic Johnson",
          "Alfred Russel Wallace",
          "Homophobie",
          "Empire State Building",
          "Processeur",
          "Strasbourg",
          "Système solaire",
          "Nestlé", "Les Aventuriers du rail", "mécanique (science)", "mécanique quantique", "automobile", "chimie",
          "trabsformations de la matière", "mathématiques", "toologie", "Catan", "mécanique (technique)", "jeu vidéo",
          "transition de phase"]


def init():
    driver.get("https://cemantix.herokuapp.com/pedantix")
    close_button = driver.find_element_by_xpath('// *[ @ id = "dialog-close"]')
    close_button.click()
    for word in littleHelp:
        guessWord(word)


def guessWord(string):
    alreadyGuessed.append(string)
    if string[-1] == 's':
        guessWord(string[:-1])
    driver.switch_to.window(driver.window_handles[0])
    driver.find_element_by_xpath('//*[@id="guess"]').send_keys(string)
    submit_button = driver.find_element_by_xpath('//*[@id="guess-btn"]')
    submit_button.click()
    if check_if_found():
        return [True, -1, string]
    result = driver.find_element_by_id("error")
    if '\U0001F7E9' in result.text or '\U0001F7E7' in result.text:
        green = 0
        for element in result.text:
            if element == '\U0001F7E9' or element == '\U0001F7E7':
                green += 1
        return [True, green, string]
    else:
        return [False, 0, string]


def guessArticle(name):
    guessList = gotoWikipediaArticle(name)
    best_word_n = 0
    best_word = 'France'
    for word in guessList:
        if word not in alreadyGuessed:
            result = guessWord(word)
            if result[0]:
                if result[1] == -1:
                    return "found_word"
                if best_word_n <= result[1] and result[-1] not in alreadyVisited:
                    best_word_n = result[1]
                    best_word = result[-1]
                else:
                    if result[1] >= 2 and result[-1] not in alreadyVisited:
                        noLuck.append(result[-1])
    if best_word_n < 2:
        best_word = noLuck[-1]
        noLuck.pop()
    return best_word


def openGoogle():
    cemantix_button = driver.find_element_by_xpath('/ html / body / aside / a[1]')
    cemantix_button.click()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://www.google.com/')
    driver.implicitly_wait(3)  # gives an implicit wait for 3 seconds
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/span/div/div/div/div[3]/div[1]/button[1]/div').click()


def gotoWikipediaArticle(name):
    alreadyVisited.append(name)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://www.google.com/')
    search_query = driver.find_element_by_name('q')
    search_query.send_keys(name + ' wikipedia')
    search_query.send_keys(Keys.RETURN)
    driver.implicitly_wait(3)  # gives an implicit wait for 3 seconds
    wiki_url = driver.find_element_by_class_name('iUh30').text.replace(' › ', '/')
    if check_invalid_url(wiki_url):
        driver.get(wiki_url)
        driver.implicitly_wait(5)  # gives an implicit wait for 5 seconds
    else:
        return []

    if check_exists_by_xpath('//*[@id="mw-content-text"]/div[1]/p[2]') and check_exists_by_xpath(
            '/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[1]') and check_exists_by_xpath(
        '/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[2]'):
        text0 = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[1]').text
        text = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div[1]/p[2]').text
        text2 = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[2]').text
        text = text + text2 + text0
        if text == '':
            text = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div[1]/p[3]').text
        text = re.findall('[a-zA-Z\u00C0-\u00FF]*', text)
        # élimine les espaces et les éléments courts
        lst = [x for x in text if x != '' and len(x) > 2]
    else:
        nextArticle = noLuck[-1]
        noLuck.pop()
        lst = gotoWikipediaArticle(nextArticle)
    return lst


def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_clickable_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath).click()
    except ElementNotInteractableException:
        return False
    return True


def check_invalid_url(url):
    try:
        driver.get(url)
    except InvalidArgumentException:
        return False
    return True


def check_if_found():
    return check_clickable_by_xpath('//*[@id="share"]')


init()
openGoogle()
nextGuess = guessArticle("Constantinople")
while True:
    nextGuess = guessArticle(nextGuess)
    if nextGuess == "found_word":
        break
    driver.switch_to.window(driver.window_handles[0])

print('Mots utilisés', alreadyGuessed)
print('Articles visités', alreadyVisited)
