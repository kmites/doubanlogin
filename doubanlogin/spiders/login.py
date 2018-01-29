# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import logging
from io import BytesIO
from PIL import Image,ImageFilter,ImageEnhance


class LoginSpider(scrapy.Spider):
    name = 'login'
    allowed_domains = ['douban.com']
    start_urls = ['https://www.douban.com/login']

    login_url =  'https://www.douban.com/login'

    form_email = 'xxx'
    form_password = 'xxx'

    def start_requests(self):

        yield Request(self.login_url,callback=self.login,dont_filter=True)

    def login(self,response):

        logging.info('Start Login!')

        captcha_url = response.xpath("//img[@id ='captcha_image']/@src").extract_first()

        if not captcha_url:

            formdata = {'form_email':self.form_email,
                        'form_password':self.form_password
                        }

            yield FormRequest.from_response(response,
                                            formdata=formdata,
                                            callback=self.login_check,
                                            dont_filte=True)
        else:
            yield Request(captcha_url,
                          callback=self.captcha_login,
                          meta={'login_response':response},
                          dont_filter=True)

    def captcha_login(self,response):
        formdata = {'form_email': self.form_email,
                    'form_password': self.form_password,
                    'captcha_field': self.get_captcha(response.body)
                    }

        yield FormRequest.from_response(response,
                                        formdata=formdata,
                                        callback=self.login_check)

    def login_check(self,response):

        title = response.xpath('//head/title/text()').extract_first()

        if title == '豆瓣':
            logging.info('Login Success!')
            return super().start_requests() #调用基类的start_requests(),爬取数据页面

        else:
            logging.info('Login Fail!')
            return self.start_requests() #重新登录

    def parse(self, response):
        pass

    # 验证码识别
    def get_captcha(self,data):
        image = Image.open(BytesIO(data))
        # image.show()

        image_enh = ImageEnhance.Brightness(image)
        image_enh_bright = image_enh.enhance(2.0)
        # image_enh_bright.show()

        image_enh = ImageEnhance.Color(image_enh_bright)
        image_enh_color = image_enh.enhance(1.5)
        # image_enh_color.show()

        image_enh = ImageEnhance.Sharpness(image_enh_color)
        image_enh_sharp = image_enh.enhance(2)
        # image_enh_sharp.show()

        image_l = image_enh_sharp.convert('L')
        # image_l.show()

        image_point = image_l.convert('1')
        #image_point.show()
        #========================='
        captcha = image_to_string(image_point)

        image.close()

        return captcha
