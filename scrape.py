from time import sleep
from splinter import Browser
from getpass import getpass
import csv

def login(browser):
    browser.fill('h_username', input('Enter opal username:') )
    browser.fill('h_password', getpass('Enter opal password:') )
    browser.find_by_css('form#homepageRegisteredLogin input[type=submit]').click()

def go2activity(browser):
    css = '.content #tab-nav li:nth-child(2) a'
    await(browser, css)
    browser.find_by_css( css ).click()

def get_pages(browser):
    yield
    css = '#pagination #next'
    await(browser, css)
    next_btn = browser.find_by_css( css )
    while len(next_btn) > 0:
        next_btn.click()
        if await(browser, css): yield
        else: return
        next_btn = browser.find_by_css( css )

def get_rows(browser):
    css = '#transaction-data tr'
    await(browser, css)
    for row in browser.find_by_css( css ):
        if len( row.find_by_css('td') ) > 0:
            yield row

def row2array(row):
    # columns:
    # transaction number, date time, mode, details, journey number, fare applied, fare, discount, amount
    columns = row.find_by_tag('td')
    # strip out <br>s, &shy and all sorts of other shit. To ascii and back again handles most of it.
    result_columns = [ column.text.replace("\n",' ').encode('ascii','ignore').decode() for column in columns ]
    img = columns[2].find_by_tag('img')
    if len(img) > 0:
        result_columns[2] = img['alt']
    return result_columns

def get_all_rows(browser):
    for page in get_pages(browser):
        for row in get_rows(browser):
            yield row2array( row )

def write_rows(browser, filename):
    with open(filename, 'wt') as csvfile:
        writer = csv.writer(csvfile)
        for row in get_all_rows(browser):
            writer.writerow( row )
            csvfile.flush()

def await(browser, css):
    for i in range(3):
        if not browser.is_element_not_present_by_css(css,1):
            return True
    return False

if __name__ == '__main__':
    browser = Browser('chrome')
    browser.visit('http://opal.com.au')
    login(browser)
    go2activity(browser)
    write_rows(browser, 'trips.csv')
