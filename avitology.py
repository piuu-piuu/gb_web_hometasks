# # Avito.ru scraper
# Собирает товары в выбранной субкатегории по заданной строке поиска
# Сохраняет в базу все местные результаты, или первую страницу выдачи,
# если местных результатов меньше 50

from datetime import datetime
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# details parser subroutine

def collect_page(driver, item):
    # all this 'try' block is for automatically droppinng an item if no seller info is present
    try:
        item_dict = {}
        item_seller = driver.find_element(
            By.XPATH, './/div[contains(@class, "item-seller")]//a')
        item_seller_link = item_seller.get_attribute('href')
        item_title = item.find_element(
            By.XPATH, './/div[contains(@class, "item-title")]').text
        item_price_string = item.find_element(
            By.XPATH, './/div[contains(@class, "item-price")]').text.replace('\u20bd', '')
        if item_price_string == 'Цена не указана':
            item_price = None
        else:
            item_price = int(item_price_string.replace(' ', ''))
        item_description = item.find_element(
            By.XPATH, './/div[contains(@class, "item-description")]').text
        item_description.replace('\xd7', 'x').replace(
            '\u20bd', 'руб.').replace('\ufffd', '?')
        item_address = item.find_element(
            By.XPATH, './/*[contains(@class, "geo")]/span').text
        item_date = item.find_element(
            By.XPATH, './/div[contains(@class, "item-date")]').text
        item_link_element = item.find_element(
            By.XPATH, './/div[contains(@class, "item-title")]/a')
        item_link = item_link_element.get_attribute('href')
        item_dict['item_title'] = item_title
        item_dict['item_price'] = item_price
        item_dict['item_description'] = item_description
        item_dict['item_address'] = item_address
        item_dict['current_date'] = datetime.today().strftime('%d-%m-%Y')
        item_dict['item_date'] = item_date
        item_dict['item_link'] = item_link
        item_dict['item_seller_link'] = item_seller_link
        return item_dict
    except Exception as e:
        print(type(e))
        return None


# main search routine

def search_avito(search_string, search_category):

    # driver starts

    chrome_options = Options()
    chrome_options.add_argument("start-maximized")

    # relative driver path does not work (win10),
    # but driver in the main folder works just fine

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.implicitly_wait(10)
        driver.get("http://www.avito.ru")

        # say yes to suggested location

        try:
            location_button = driver.find_element(
                By.XPATH, '//button[@data-marker="location/tooltip-agree"]')
            location_button.click()
        except Exception as e:
            print(type(e))

            # the search

        search_field = driver.find_element(
            By.XPATH, '//input[@type="text"]')
        search_field.send_keys(search_string)
        search_field.send_keys(Keys.RETURN)

        # the subcategory extraction

        xpath_str = '//a[contains(@class, "rubricator-list") and @title ="' + \
            search_category + '"]'
        avito_category = driver.find_element(By.XPATH, xpath_str)
        category_link = avito_category.get_attribute('href')
        try:
            driver.get(category_link)
        except Exception as e:
            print(type(e))

        # items' count --> number of pages, max 50 items per page

        count = driver.find_element(
            By.XPATH, '//span[contains(@class, "page-title-count")]').text
        count = int(count.replace(' ', ''))
        count = round(count/50)

        # page link template

        paginator = driver.find_element(
            By.XPATH, '//a[contains(@class, "pagination-page")]')
        link_template = paginator.get_attribute('href')

        # collecting pages,
        # 50 elements per page,
        # promotions excluded (hint: no seller information)

        # page 1

        page_list = []
        all_items = driver.find_elements(
            By.XPATH, '//div[@data-marker = "item"]')
        for item in all_items:
            item_dict = collect_page(driver, item)
            if item_dict:
                page_list.append(item_dict)

        # are there more?

        if count > 1:
            for i in range(2, count+1):
                page_link = link_template + '&p=' + str(i)
                driver.get(page_link)
                all_items = driver.find_elements(
                    By.XPATH, '//div[@data-marker = "item"]')
                for item in all_items:
                    item_dict = collect_page(driver, item)
                    if item_dict:
                        page_list.append(item_dict)

    return page_list


if __name__ == '__main__':
    # search string and subcategory
    what = 'Зенит'
    where = 'Плёночные фотоаппараты'
    pprint(len(search_avito(what, where)))
