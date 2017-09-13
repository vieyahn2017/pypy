# -*- coding: utf-8 -*-
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import time
import sys
# reload(sys)
# sys.setdefaultencoding( "utf-8" )

def crawl_cnblogs(blog_url,username,pwd):

    driver = webdriver.PhantomJS()

    driver.get("http://passport.cnblogs.com/user/signin?ReturnUrl=http%3A%2F%2Fwww.cnblogs.com%2F")
    wait = ui.WebDriverWait(driver, 10)
    wait.until(lambda dr: dr.find_element_by_id('signin').is_displayed())
    driver.find_element_by_id("input1").send_keys(username)
    driver.find_element_by_id("input2").send_keys(pwd)
    driver.find_element_by_id("signin").click()
    wait.until(lambda dr: dr.find_element_by_id('login_area').is_displayed())

    driver.get(blog_url)
    wait.until(lambda dr: dr.find_element_by_id('mainContent').is_displayed())
    time.sleep(3)
    #articles = driver.find_element_by_xpath('//div[@class="postTitle"]/a')
    articles = driver.find_elements_by_class_name("postTitle")
    for article in articles:
        print article
        print article.text.encode('gb18030') #.decode("utf-8", "ignore")
        # scrapy爬虫之爬取汽车信息 编码居然错误 

    urls = driver.find_elements_by_class_name("postTitle2")
    for url in urls:
        print url.get_attribute("href")

    #driver.save_screenshot('screen.png')
    driver.quit()


def netease(url,username,pwd):
    driver = selenium.PhantomJS()
    driver.get("http://mail.163.com/")
    wait = ui.WebDriverWait(driver, 10)
    driver.find_element_by_xpath('')


if __name__ == '__main__':
    crawl_cnblogs("http://www.cnblogs.com/xiaoyy3/", "username", "password@")
