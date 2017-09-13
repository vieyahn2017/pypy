from celery_config import app

import scrapy
import requests

def get_elems_by_xpath(html, xpath):
    sel = scrapy.Selector(text=html)
    return sel.xpath(xpath).extract()

@app.task
def crawl():
    url = 'http://bigdata.51cto.com/'
    html =requests.get(url).content
    # titles = get_elems_by_xpath(html, '//div[@class="list_leftcont"]/div/div[@class="list_leftcont01"]/h4/a/text()')
    # for title in titles:
    #     print title.decode('utf-8')
    #
    # #code problem ~!~~~!

    times = get_elems_by_xpath(html, '//div[@class="list_leftcont"]/div/div[@class="list_leftcont01"]/p[@class="timeline"]/span[1]/text()')
    for time in times:
        print time