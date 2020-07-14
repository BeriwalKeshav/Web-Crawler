import scrapy
import re
import os
import json
import requests
class PepperFrySpider(scrapy.Spider):
    name="pepper"
    BASE_DIR='./Pepperfry_data/'
    MAX_CNT=20
    
    def start_requests(self):
        BASE_URL="https://www.pepperfry.com/site_product/search?q="
        items = ["two seater sofa","bench","book cases","coffee table","dining set","queen beds","arm chairs","chest drawers","garden seating","bean bags","king beds"]
        urls=[]
        dir_names=[]
        
        for item in items:
            query_string = '+'.join(item.split(' '))
            dir_name = '-'.join(item.split(' '))
            dir_names.append(dir_name)
            urls.append(BASE_URL+query_string)
            
            dir_path = self.BASE_DIR+dir_name
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        for i in range(len(urls)):
            d = {
               "dir_name": dir_names[i]
            }
            resp =  scrapy.Request(url=urls[i],callback=self.parse,dont_filter=True)
            resp.meta['dir_name'] = dir_names[i]
            yield resp
            
    def parse(self, response,**meta):
        product_urls=response.css('div[class=card-img-wrp\ center-xs\ card-srch-img-wrp] a::attr(href)').getall()
        counter = 0
        for url in product_urls[::2]:
            print(url)
            resp =  scrapy.Request(url=url,callback=self.parse_item,dont_filter=True)
            resp.meta['dir_name'] = response.meta['dir_name']
            if counter == self.MAX_CNT:
                break

            if not resp == None:
                counter +=1
            yield resp
            
    def parse_item(self,response,**meta):
        item_title=response.css('h1[class=v-pro-ttl\ pf-medium-bold-text]::text').get()
        image_url=response.css('ul[class=vipImage__thumb-slider\ horizontal]')
        image_url_list=image_url.css('li[class=vipImage__thumb-each\ noClickSlide] a::attr(data-img)').getall() 
        CATEGORY_NAME = response.meta['dir_name']
        ITEM_DIR_URL = os.path.join(self.BASE_DIR,os.path.join(CATEGORY_NAME,item_title))  
        if not os.path.exists(ITEM_DIR_URL):
            os.makedirs(ITEM_DIR_URL)
            
        for i,img_url in enumerate(image_url_list):
            r = requests.get(img_url)
            with open(os.path.join(ITEM_DIR_URL,"image_{}.jpg".format(i)),'wb') as f:
                f.write(r.content)
            