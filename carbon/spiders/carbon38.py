import re
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Carbon38Spider(scrapy.Spider):
    name = "carbon38"
    allowed_domains = ["carbon38.com"]
    start_urls = [
        "https://carbon38.com/en-in/collections/tops?filter.p.m.custom.available_or_waitlist=1"
    ]

    def __init__(self, *args, **kwargs):
        super(Carbon38Spider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        cards = response.css('.ProductItem__Wrapper')

        for card in cards:
            link = card.css("a::attr(href)").get()

            if link:
                yield response.follow(
                    link,
                    callback=self.parse_product
                )

        next_page = response.css('[rel="next"]::attr(href)').get()
        
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        image_url = response.css('.AspectRatio.AspectRatio--withFallback img::attr(src)').get()
        brand = response.css(".ProductMeta__Vendor a::text").get()
        product_name = response.css('.ProductMeta__Title::text').get()
        price = response.css('.ProductMeta__Price .Price::text').get()
        color = response.css('.ProductForm__SelectedValue::text').get()
        image_urls = response.css('.AspectRatio.AspectRatio--withFallback img::attr(src)').getall()
        sizes = list(set(response.css(".SizeSwatch::text").getall()))
        
        description = ' '.join(response.css('.Faq__Answer.Rte p::text').getall())  or 'No description available'
        review = self.get_review(response.url)

        if image_urls:
            image_urls = [response.urljoin(url) for url in image_urls]

        if not brand:
            brand = response.css('.ProductMeta__Vendor::text').get()

        yield {
            "primary_image_url": response.urljoin(image_url),
            "brand": brand,
            "product_name": product_name.strip() if product_name else None,
            "price": price.strip() if price else None,
            "reviews": review,
            "Colour": color.strip() if color else None,
            "sizes": sizes,
            "description":description.strip(),
            "product_url": response.url,
            "image_urls": image_urls
        }

    def get_review(self, url):
        self.driver.get(url)
        review_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.yotpo-bottom-line-basic-text'))
        )

        review = review_element.text
        match = re.search(r"(\d+\s\w+)", review)
        if match:
            return  match.group()
        else:
            return "0 Reviews"

    def closed(self, reason):
        self.driver.quit()
