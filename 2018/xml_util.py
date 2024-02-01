# coding=utf-8
from xml.etree import ElementTree
import sys

# 如果出现一些简单的编码错误，可以去掉这两句的注释
# reload(sys)
# sys.setdefaultencoding('utf8')


class XMLParser(object):
    """
    XML解析公共方法类
    2018.4.17
    """

    def __init__(self, txt, is_log=False):
        if is_log:
            print "the raw xml: ", txt, "=============\n"
        self.xml = ElementTree.fromstring(txt.strip())

    def get_etree_from_txt(self, txt):
        """ 前一个版本的 def __init__(self, txt): """
        # print "the raw xml: ", txt, "=============\n"
        parser = ElementTree.XMLParser()
        parser.feed(txt.strip())
        xml_element = parser.close()
        return xml_element
        # tree = ElementTree.ElementTree(xml_element)
        # return tree.getroot()

    def get_root(self):
        return self.xml

    def get_element(self, xml=None, element='/'):
        if xml is None:
            xml = self.xml
        if element == '/':
            return xml
        data = xml.find(element)
        try:
            return data
        except AttributeError:
            raise Exception('{0} element not exist in xml'.format(element))

    def get_elements(self, xml, element):
        data_list = xml.findall(element)
        results = []
        try:
            for data in data_list:
                results.append(data)
                # results.append({"text": data.text, "attrib": data.attrib})
            return results
        except AttributeError:
            raise Exception('{0} element not exist in xml'.format(element))

    def get_element_with_path(self, xml, element='/', path_separator='/'):
        element_list = element.split(path_separator)
        for e in element_list[:-1]:
            xml = xml.find(e)
        return self.get_element(xml, element_list[-1])

    def get_elements_with_path(self, xml, element, path_separator='/'):
        element_list = element.split(path_separator)
        for e in element_list[:-1]:
            xml = xml.find(e)
        return self.get_elements(xml, element_list[-1])




xml_test = """   
<?xml version='1.0' encoding='utf-8'?>
<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<!-- The contents of this file will be loaded for each web application -->
<Context  antiResourceLocking="false" privileged="true" >

    <!-- Default set of monitored resources -->
    <WatchedResource trial="true">WEB-INF/web.xml
	<x y="1">x3</x>
	<x y='2' z='3'>x4</x>
	<x y='3' z='4' w='5'>x5</x>
    </WatchedResource>

    <!-- Uncomment this to disable session persistence across Tomcat restarts -->
    <!--
    <Manager pathname="" />
    -->

    <!-- Uncomment this to enable Comet connection tacking (provides events
         on session expiration as well as webapp lifecycle) -->
    <!--
    <Valve className="org.apache.catalina.valves.CometConnectionManagerValve" />
    -->

</Context>  
"""

if __name__ == "__main__":
    xml_parser = XMLParser(xml_test)
    context_xml = xml_parser.get_root()

    WatchedResource = xml_parser.get_element(context_xml, "WatchedResource")
    print WatchedResource
    print WatchedResource.tag # Tag名字
    trial = WatchedResource.attrib.get('trial')  #取属性
    print trial
    print WatchedResource.attrib.has_key('trial')  # 是否存在属性
    print WatchedResource.attrib.has_key('noexist')  # 是否存在属性

    print xml_parser.get_elements(context_xml.find("WatchedResource"), "x")  # list
    print xml_parser.get_element_with_path(context_xml, "WatchedResource/x")
    print xml_parser.get_elements_with_path(context_xml, "WatchedResource/x")



