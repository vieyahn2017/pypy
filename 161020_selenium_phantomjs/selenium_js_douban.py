# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import sys
import datetime
import time
from selenium import webdriver
import selenium.webdriver.support.ui as ui

def get_elems_by_xpath(html, xpath):
    sel = scrapy.Selector(text=html)
    return sel.xpath(xpath).extract()

def main1():
    url = 'https://movie.douban.com/explore'
    response = requests.get(url)
    html = response.content
    #print html

    #items = get_elems_by_xpath(html, '//a[@class="item"]') 
    #infos = get_elems_by_xpath(html, '//div[@class="cover-wp"]')
    info_images = get_elems_by_xpath(html, '//div[@class="cover-wp"]/img/@src')
    info_titles = get_elems_by_xpath(html, '//div[@class="cover-wp"]/img/@alt')    

    items = {}
    for title, image in zip(info_titles, info_images):
        items['item'] = {"title": title, "image": image}

    print items  # empty


def main():
    url = 'https://movie.douban.com/explore'
    driver = webdriver.PhantomJS()
    driver.get(url)
    wait = ui.WebDriverWait(driver, 10)
    wait.until(lambda dr: dr.find_element_by_xpath('//div[@class="list-wp"]').is_displayed())

    js="""
                $('.more').click();
    """
    jsss="""
                   (function(){
                     setTimeout("$('.more').click()", 2000);
                     //console.log($('.cover-wp').length); //不断执行点击（更多），暂时还不能实现
                   })();"""
    driver.execute_script(js)
    time.sleep(2)

    infos = driver.find_elements_by_xpath('//div[@class="cover-wp"]/img')
    items = []
    for x in infos:
        image = x.get_attribute("src")
        title = x.get_attribute("alt")
        items.append({"title": title, "image": image})

    print items

    # infos =  driver.find_elements_by_class_name('cover-wp')
    # items = []
    # for x in infos:
    #     image = x.find_element_by_tag_name('img').get_attribute("src")
    #     title = x.find_element_by_tag_name('img').get_attribute("alt")
    #     items.append({"title": title, "image": image})
    # print items



if __name__ == "__main__":
    main()
