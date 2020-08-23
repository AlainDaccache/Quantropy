import re
import xml.etree.ElementTree as ET
import requests
url = 'https://www.sec.gov/Archives/edgar/data/1326801/000132680118000009/fb-20171231.xml'
response = requests.get(url).text
elements = ET.fromstring(response)
for element in elements.iter():
    if 'contextRef' in element.attrib.keys():
        tag_name = re.sub(r"(\w)([A-Z])", r"\1 \2", element.tag.split('}')[1])
        try:
            tag_value = int(element.text)
        except:
            continue
        tag_date = element.attrib['contextRef']
        print(element.attrib['contextRef'])

