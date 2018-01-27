# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import sys
import argparse
import datetime


# 原文件的思想还可以，大概网站改版了，好多不能用了
# 我换个网站按这思想来测试


def saver(obj, file):
    obj.update(count=str(len(obj)))
    obj.update(last_update=str(datetime.datetime.today()))
    with open(file, "w") as f:
        f.write(json.dumps(obj))


def loader(file):
    with open(file, "r") as f:
        return json.loads(f.read())


def comparer(new, saved):
    for k,v in new.iteritems():
        if k in saved:
            if new[k]["entries"] != saved[k]["entries"]:
                print "We have one new(or more|or less) record in '{0}' entry! Old was {1}. New is {2}. See it here {3}{4}".format(k, saved[k]["entries"], new[k]["entries"], const['DRIVE_URL'], new[k]["page_link"]) 
        else:
            print "We have new one car from {0}. See it here {1}{2}".format(k, const['DRIVE_URL'], new[k]["page_link"])
    saver(new, const['DB_FILE'])


def get_all_cars(url):
    all_html = ""
    start = 0
    while True:
        u = "{}{}".format(url, start)
        print u
        resp = requests.get(u)
        resp_json = json.loads(resp.text)
        all_html += resp_json["html"]
        if "start" in resp_json:
            start = resp_json["start"]
        else:
            break 
    return all_html


def get_elems_by_xpath(html, xpath):
    sel = scrapy.Selector(text=html)
    return sel.xpath(xpath).extract()


def prepare_dict():
    html = get_all_cars(const['SEARCH_URL'])
    titles = get_elems_by_xpath(html, '//span[contains(@class,"uname uname-color")]/text()')
    entries = get_elems_by_xpath(html, u'//span[@data-tt="Записей в бортжурнале"]/text()')
    hrefs = get_elems_by_xpath(html, '//div[@class="carcard-caption"]/a/@href')
    
    saved = {}
    for t, e, p  in zip(titles, entries, hrefs):
        saved[t] = {"entries": e, "page_link": p}

    return saved


#  以上的代码是从俄语汽车网站爬取数据的代码，我的代码只用到
#  def get_elems_by_xpath(html, xpath):
#   改写了自己的main()

def main():
    url = 'http://graphite.readthedocs.io/en/latest/overview.html'
    response = requests.get(url)
    html = response.content
    #print html
    titles = get_elems_by_xpath(html, '//li[@class="toctree-l1"]/a/text()')
    hrefs = get_elems_by_xpath(html, '//li[@class="toctree-l1"]/a/@href')
    # <li class="toctree-l1"><a class="reference internal" href="faq.html">FAQ</a></li>
    # <li class="toctree-l1"><a class="reference internal" href="install.html">Installing Graphite</a></li>

    items = {}
    for title, href  in zip(titles, hrefs):
        page_root = 'http://graphite.readthedocs.io/en/latest/'
        html_content = requests.get(page_root + href).content
        content = get_elems_by_xpath(html_content, '//div[@itemprop="articleBody"]')[0]
        items[title] = {"page_link": href, "page_content": content}

    # print items
    # print items.keys()
    # print items.values()

    # for key in items.values():
    #     f = open(key['page_link'] , 'w')
    #     f.write(key['page_content'])
    #     f.close()
    # 初步功能实现，不过某些记录会出编码问题
    # UnicodeEncodeError: 'ascii' codec can't encode character u'\u2019' in position 12: ordinal not in range(128)

    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    import codecs

    for key in items.values():
        if key['page_link'].find("#") == -1:
            file_ = codecs.open('graphite/' + key['page_link'], "w", "utf-8") #graphite文件夹必须存在，否则出错
            file_.write(key['page_content'])
            print key['page_link'] + '  having saved!'
            file_.close()


if __name__ == "__main__":
    main()
