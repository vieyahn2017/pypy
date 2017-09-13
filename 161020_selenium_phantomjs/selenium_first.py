# -*- coding: utf-8 -*-
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
import os
import time


def chrome_test():
    # driver = webdriver.Chrome()
    # Paste the chromedriver.exe file in "C:\Python27\Scripts" Folder.
    # For windows, please have the chromedriver.exe placed under <Install Dir>/Python27/Scripts/
    # # or
    # chromedriver = "/Users/adam/Downloads/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(chromedriver)
    
    # driver.get("http://stackoverflow.com")
    # driver.quit()

    browser = webdriver.Chrome()
    browser.get("http://www.baidu.com")
    time.sleep(2)

    print "浏览器最大化"
    browser.maximize_window()  #将浏览器最大化显示
    time.sleep(2)

    browser.find_element_by_id("kw").send_keys("selenium")
    browser.find_element_by_id("su").click()
    time.sleep(3)
    browser.quit()


def firefox_test():
    browser = webdriver.Firefox()
    # browser = webdriver.Firefox(executable_path = '/Users/jinwenxin/desktop/pythonPractice/geckodriver')
    # 教大家一个方法，我用了在python下执行了help(webdriver.Firefox) 回车，这样就知道了传什么参数。

    browser.get("http://www.baidu.com")
    time.sleep(2)

    print "浏览器最大化"
    browser.maximize_window()  #将浏览器最大化显示
    time.sleep(2)

    browser.find_element_by_id("kw").send_keys("selenium")
    browser.find_element_by_id("su").click()
    time.sleep(3)
    browser.quit()


def  firefox_test23():
    browser = webdriver.Firefox()
    browser.get("http://m.mail.10086.cn")
    time.sleep(2)
    print "设置浏览器宽480、高800显示"
    browser.set_window_size(480, 800)  #参数数字为像素点
    time.sleep(3)
    browser.quit()

    browser = webdriver.Firefox()
    #访问百度首页
    first_url= 'http://www.baidu.com'
    print "now access %s" %(first_url)
    browser.get(first_url)
    time.sleep(2)
    #访问新闻页面
    second_url='http://news.baidu.com'
    print "now access %s" %(second_url)
    browser.get(second_url)
    time.sleep(2)
    #返回（后退）到百度首页
    print "back to  %s "%(first_url)
    browser.back()
    time.sleep(1)
    #前进到新闻页
    print "forward to  %s"%(second_url)
    browser.forward()
    time.sleep(2)

    browser.quit()


def  chrome_some_test23():

    driver = webdriver.Chrome()

    driver.find_element_by_xpath("//input[@id='kw']").send_keys("selenium")
    #  input标签下id =kw的元素
    driver.find_element_by_xpath("//div[@id='fm']/form/span/input").send_keys("selenium")
    # 在/form/span/input 层级标签下有个div标签的id=fm的元素
    driver.find_element_by_xpath("//tr[@id='check']/td[2]").click() 
    # id为'check' 的tr ，定闪他里面的第2个td
    driver.find_element_by_xpath("//input").send_keys("selenium") 
    driver.find_element_by_xpath("//tr[7]/td[2]").click()
    # 第7个tr 里面的第2个td
    driver.find_element_by_xpath("//a[contains(text(),'网页')]").click()
    # 在a标签下有个文本（text）包含（contains）'网页' 的元素
    driver.find_element_by_xpath("//a[@href='http://www.baidu.com/']").click()
    # 有个叫a的标签，他有个链接href='http://www.baidu.com/ 的元素
    print driver.find_element_by_id('result').text.split('\n')[0].split('来自：')[1]

    # 选择页面上所有的input，然后从中过滤出所有的checkbox并勾选之
    inputs = dr.find_elements_by_tag_name('input')
    for input in inputs:
        if input.get_attribute('type') == 'checkbox':
            input.click()


    file_path =  'file:///' + os.path.abspath('checkbox.html')
    dr.get(file_path)

    # 选择所有的checkbox并全部勾上
    checkboxes = dr.find_elements_by_css_selector('input[type=checkbox]')
    for checkbox in checkboxes:
        checkbox.click()
    time.sleep(2)
    # 把页面上最后1个checkbox的勾给去掉
    driver.find_elements_by_css_selector('input[type=checkbox]').pop().click()
    # 打印当前页面上有多少个checkbox
    print len(dr.find_elements_by_css_selector('input[type=checkbox]'))
    time.sleep(2)


    #点击Link1链接（弹出下拉列表）
    driver.find_element_by_link_text('Link1').click()
    #找到id 为dropdown1的父元素
    WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('dropdown1').is_displayed())
    #在父亲元件下找到link为Action的子元素
    menu = driver.find_element_by_id('dropdown1').find_element_by_link_text('Action')
    #鼠标定位到子元素上
    webdriver.ActionChains(driver).move_to_element(menu).perform()


    driver.get("http://www.baidu.com")
    driver.find_element_by_id("kw").clear()
    driver.find_element_by_id("kw").send_keys("selenium")
    driver.find_element_by_id("su").click()


    driver.find_element_by_id("kw").send_keys("selenium")
    time.sleep(2)
    #通过submit() 来操作
    driver.find_element_by_id("su").submit()


    select = driver.find_element_by_tag_name("select")
    allOptions = select.find_elements_by_tag_name("option")
    for option in allOptions:
        print "Value is: " + option.get_attribute("value")
        option.click()


    driver.get("http://www.baidu.com")
    time.sleep(2)
    #有时候不是一个输入框也不是一个按钮，而是一个文字链接，我们可以通过link    
    driver.find_element_by_link_text("贴 吧").click()
    driver.find_element_by_partial_link_text("贴").click()
    #通过find_element_by_partial_link_text() 函数，我只用了“贴”字，脚本一样找到了"贴 吧" 的链接
    time.sleep(2)
    driver.quit()

    driver.implicitly_wait(30)
    #先找到到ifrome1（id = f1）
    driver.switch_to_frame("f1")
    #再找到其下面的ifrome2(id =f2)
    driver.switch_to_frame("f2")

    driver.get("http://passport.kuaibo.com/login/?referrer=http%3A%2F%2Fvod.kuaibo.com%2F%3Ft%3Dhome")
    #给用户名的输入框标红
    js="var q=document.getElementById(\"user_name\");q.style.border=\"1px solid red\";"
    #调用js
    driver.execute_script(js)
    time.sleep(3)
    driver.find_element_by_id("user_name").send_keys("username")
    driver.find_element_by_id("user_pwd").send_keys("password")
    driver.find_element_by_id("dl_an_submit").click()
    time.sleep(3)


    #######通过JS 隐藏选中的元素#########
    #第一种方法：
    driver.execute_script('$("#tooltip").fadeOut();')
    time.sleep(5)

    #第二种方法：
    button = driver.find_element_by_class_name('btn')
    driver.execute_script('$(arguments[0]).fadeOut()',button)
    time.sleep(5)


    #脚本要与upload_file.html同一目录
    file_path =  'file:///' + os.path.abspath('upload_file.html')
    driver.get(file_path)
    #定位上传按钮，添加本地文件
    driver.find_element_by_name("file").send_keys('D:\\selenium_use_case\upload_file.txt')
    time.sleep(2)



    driver.get("http://m.mail.10086.cn")
    driver.implicitly_wait(30)
    #登陆
    driver.find_element_by_id("ur").send_keys("手机号")
    driver.find_element_by_id("pw").send_keys("密码")
    driver.find_element_by_class_name("loading_btn").click()
    time.sleep(3)

    #进入139网盘模块
    driver.find_element_by_xpath("/html/body/div[3]/a[9]/span[2]").click()
    time.sleep(3)
    #上传文件
    driver.find_element_by_id("id_file").send_keys('D:\\selenium_use_case\upload_file.txt')
    time.sleep(5)



    driver.quit()


#执行该文件的主过程
if __name__ == '__main__':
    chrome_test()  # success

    # firefox_test()  # fail
    # #selenium.common.exceptions.WebDriverException: Message: 
    # #Expected browser binary location, but unable to find binary in default location, 
    # #no 'moz:firefoxOptions.binary' capability provided, and no binary flag set on the command line


    #hiBlog("你的博客地址","xiaoyaoyou3","222959cn@")