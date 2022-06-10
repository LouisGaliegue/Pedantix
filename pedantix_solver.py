"""This program tries to find the solution to the daily pedantix (https://cemantix.herokuapp.com/pedantix).

Usage:
======
    python pedantix_solver.py

    FIREFOX_LOCATION needs to be specified in the file
    GECKO_DRIVER needs to be downloaded (https://github.com/mozilla/geckodriver/releases) and its location specified in
    the file.

"""

__authors__ = ("Louis Galiègue")
__contact__ = ("louis.galiegue@eleves.enpc.fr")
__date__ = "2022-06-09"

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, InvalidArgumentException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import re
import time

"""Specify here FIREFOX_LOCATION and GECKO_DRIVER

"""

FIREFOX_LOCATION = r'C:\Program Files\Mozilla Firefox\firefox.exe'
GECKO_DRIVER = r'C:\Users\galie\Desktop\OGAME\geckodriver.exe'

"""Tables initialization

"""

LITTLE_HELP = ["France", "le", "la", "l", "les", "une", "un", "de", "du", "des", "d", "a", "à", "ou", "est", "et",
               "après",
               "avant", "par", "il", "ils", "elle", "elles", "en", "laquelle", "lequel", "lorsque", "quand", "encore"]
already_guessed = []
already_visited = []
no_luck = []
test = ["politique", "cyclisme", "football", "fonction d'onde", "religion", "physique", "science",
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
    """Initialization function. Opens the pedantix website and sends first usual words in LITTLE_HELP.
    """
    driver.get("https://cemantix.herokuapp.com/pedantix")
    close_button = driver.find_element_by_xpath('// *[ @ id = "dialog-close"]')
    close_button.click()
    for word in LITTLE_HELP:
        guess_word(word)


def guess_word(string):
    """A function that guesses a word in pedantix. Analyses the score given by the website.

    Parameters
    -----------
    string: str
        The word to guess

    Returns
    -----------
    [boolean,int,string]
        boolean: True if the word a good guess (orange or green)
        int: Number of green and orange square
        string: Word guessed

    """
    already_guessed.append(string)
    if string[-1] == 's':
        guess_word(string[:-1])
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


def guess_article(name):
    """A function that guesses the words in an article. Returns the best scoring word and stores good scoring words (
    >2 green/orange squares) in no_luck.

        Parameters
        -----------
        name: str
            The article to analyze

        Returns
        -----------
        best_word: str
            The best scoring word found in the article if no scoring words the next one in no_luck. If no_luck is empty,
            it sends a random article.

        """
    guess_list = go_to_wikipedia_article(name)
    best_word_n = 0
    best_word = 'France'
    for word in guess_list:
        if word not in already_guessed:
            result = guess_word(word)
            if result[0]:
                if result[1] == -1:
                    return "found_word"
                if best_word_n <= result[1] and result[-1] not in already_visited:
                    best_word_n = result[1]
                    best_word = result[-1]
                else:
                    if result[1] >= 2 and result[-1] not in already_visited:
                        no_luck.append(result[-1])
    if best_word_n < 2:
        if len(no_luck) > 0:
            best_word = no_luck[-1]
            no_luck.pop()
        else:
            go_to_random_article(read=False)
            best_word = driver.find_element_by_xpath('//*[@id="firstHeading"]').text
    return best_word


def open_google():
    """A function that opens google in a new tab."""
    cemantix_button = driver.find_element_by_xpath('/ html / body / aside / a[1]')
    cemantix_button.click()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://www.google.com/')
    driver.implicitly_wait(3)  # gives an implicit wait for 3 seconds
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/span/div/div/div/div[3]/div[1]/button[1]/div').click()


def go_to_wikipedia_article(name):
    """A function that goes to a given wikipedia article.

    Parameters
    ----------
    name: str
        Name of the article to go to

    Returns
    --------
    lst: string list
        The words in the first 3 paragraphs of the article.

    """
    already_visited.append(name)
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
        return reads_article()
    else:
        return []


def go_to_random_article(read=True):
    """A function that goes to a random Wikipedia article

    Parameters
    ----------
    read: boolean (default=True)
        If True, reads the article

    Returns
    ----------
    lst: string list
        A list containing the words in the first 3 paragraphs.

    """
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard')
    driver.implicitly_wait(3)
    if read:
        return reads_article()


def reads_article():
    """A function that reads the first three paragraphs of a wikipedia article. Checks if the format is correct.

    Returns
    ----------
    lst: string list
        A list containing the words of the first 3 paragraphs.

    """
    driver.implicitly_wait(3)
    if check_exists_by_xpath('//*[@id="mw-content-text"]/div[1]/p[2]') and (check_exists_by_xpath(
            '/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[1]') and check_exists_by_xpath(
        '/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[2]')):
        text0 = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[1]').text
        text = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div[1]/p[2]').text
        text2 = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/main/div[3]/div[3]/div[1]/p[2]').text
        text = text + text2 + text0
        if text == '':
            text = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div[1]/p[3]').text
        text = re.findall('[a-zA-Z\u00C0-\u00FF]*', text)
        # no space and short elements
        lst = [x for x in text if x != '' and len(x) > 2]
    else:
        if len(no_luck) > 0:
            next_article = no_luck[-1]
            no_luck.pop()
            lst = go_to_wikipedia_article(next_article)
        else:
            lst = go_to_random_article()

    return lst


def check_exists_by_xpath(xpath):
    """A function that tries to find if an element is present with its xpath

    Parameters
    ----------
    xpath: str
        The XPath to try

    Returns
    ----------
    Boolean
        True if found, False otherwise

    """
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_clickable_by_xpath(xpath):
    """A function that tries to find if an element is clickable with its xpath

        Parameters
        ----------
        xpath: str
            The XPath to try

        Returns
        ----------
        Boolean
            True if clickable, False otherwise

        """
    try:
        driver.find_element_by_xpath(xpath).click()
    except ElementNotInteractableException:
        return False
    return True


def check_invalid_url(url):
    """A function that tries to find if an url is correct

        Parameters
        ----------
        url: str
            The url to try

        Returns
        ----------
        Boolean
            True if correct, False otherwise

        """
    try:
        driver.get(url)
    except InvalidArgumentException:
        return False
    return True


def check_if_found():
    """A function that checks if the answer is found. To be used on the pedantix page.

        Returns
        ----------
        Boolean
            True if found, False otherwise

        """
    return check_clickable_by_xpath('//*[@id="share"]')


def time_convert(sec):
    """Converts the given second time in hours/minutes/seconds and prints it.

    Parameters
    -----------
    sec: int
        Time in seconds

    """
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    print("Time Lapsed to find the article= {0}:{1}:{2}".format(int(hours), int(mins), sec))


if __name__ == "__main__":
    # Program starts here
    options = Options()
    options.binary_location = FIREFOX_LOCATION
    driver = webdriver.Firefox(executable_path=GECKO_DRIVER, options=options)
    driver.maximize_window()  # For maximizing window

    start_time = time.time()
    init()
    open_google()
    nextGuess = guess_article("Transition de phase")
    while True:
        nextGuess = guess_article(nextGuess)
        if nextGuess == "found_word":
            end_time = time.time()
            time_lapsed = end_time - start_time
            time_convert(time_lapsed)
            break
        driver.switch_to.window(driver.window_handles[0])

    print('Number of articles visited', len(already_visited), '\nArticles visited', already_visited)
