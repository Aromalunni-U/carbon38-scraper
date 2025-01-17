import scrapy

class Carbon38Spider(scrapy.Spider):
    name = "carbon38"
    allowed_domains = ["carbon38.com"]
    start_urls = [
        "https://carbon38.com/en-in/collections/tops?filter.p.m.custom.available_or_waitlist=1"
    ]

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
        sizes =  list(set(response.css(".SizeSwatch::text").getall()))

        review = response.css('.yotpo-bottom-line-basic-text::text').get()



        if image_urls:
            image_urls = [response.urljoin(url) for url in image_urls]

        if not brand:
            brand = response.css('.ProductMeta__Vendor::text').get()
        

        yield {
            "primary_image_url":response.urljoin(image_url),
            "brand":brand,
            "product_name": product_name.strip() if product_name else None,
            "price": price.strip() if price else None,
            "reviews": review.strip() if review else "0 Reviews",
            "Colour": color.strip() if color else None,
            "sizes":sizes,
            "product_url": response.url,
            "image_urls": image_urls
        }