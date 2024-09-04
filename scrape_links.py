import subprocess, argparse, scrapy
from scrapy.crawler import CrawlerProcess
from pydispatch import dispatcher


class ScrapeLinks(scrapy.Spider):
    name = "scrape_links"

    def __init__(self, *args, **kwargs):
        super(ScrapeLinks, self).__init__(*args, **kwargs)

        self.start_urls = ["https://www.cizgidiyari.com/forum/login/"]
        self.list_topic_url = kwargs["url"]

        self.user = kwargs["user"]
        self.pw = kwargs["pw"]

        try:
            self.out = kwargs["out"]
        except KeyError:
            self.out = "links.txt"

        dispatcher.connect(self.spider_quit, scrapy.signals.spider_closed)

        # Accumulate found links in a list
        self.mediafire_links = []
        self.mega_links = []

    def make_requests_from_url(self, url):
        request = super(ScrapeLinks, self).make_requests_from_url(url)
        request.cookies = self.cookies
        return request

    def parse(self, response):
        # Handle login
        
        # Check if the user is logged in
        if self.user not in response.text:
            # Log in
            xf_token = response.css('input[name="_xfToken"]').css('::attr(value)').get()
            
            form_data = {
                "login": self.user,
                "password": self.pw,
                "remember": "1",
                "_xfToken": xf_token,
                "_xfRedirect": self.list_topic_url  # Redirect to the list topic after logging in
            }
            
            return scrapy.FormRequest.from_response(
                response,
                formdata=form_data,
                callback=self.parse_list_topic
            )
        else:
            # Already logged in
            return self.parse_list_topic(response)

    def parse_list_topic(self, response):
        # The url is expected to be a link to a ÇizgiDiyarı forum topic,
        #   whose first post lists other forum topics with MediaFire or MEGA links
        #   in their first posts.

        # Get first post & all hrefs from the first post
        first_post = response.css("article.message-body")[0]
        hrefs = first_post.css('a').css('::attr(href)').getall()
            
        for href in hrefs:
            # Check if the href is a link to a forum topic
            if "/forum/" in href and "/forum/k/" not in href:
                yield response.follow(href, callback=self.parse_topic)

    def parse_topic(self, response):
        # The url is expected to be a link to a ÇizgiDiyarı forum topic
        #   with a MediaFire or MEGA link in its first post

        # Get first post & all hrefs from the first post
        first_post = response.css("article.message-body")[0]
        hrefs = first_post.css('a').css('::attr(href)').getall()

        for href in hrefs:
            # Check if the href is a MediaFire or MEGA link
            if "mediafire.com" in href:
                self.mediafire_links.append(href)
            if "mega.nz" in href:
                self.mega_links.append(href)

    def spider_quit(self, spider):
        # Save the found links to a file
        with open(self.out, "w") as f:
            for link in self.mediafire_links:
                f.write(link + "\n")
            for link in self.mega_links:
                f.write(link + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gather download links from a ÇizgiDiyari post - Cizgidiyari postundan indirme linklerini topla")
    parser.add_argument("url", help="The URL of the post to scrape - Scrapelenecek sirali liste postunun URL'si")
    parser.add_argument("user", help="The username to log in with - Cizgidiyari kullanici adi")
    parser.add_argument("pw", help="The password to log in with - Cizgidiyari hesap sifresi")
    parser.add_argument("out", nargs="?", default="links.txt", help="The file to save the links to - Linklerin kaydedilecegi dosya")

    process = CrawlerProcess()
    process.crawl(ScrapeLinks, **vars(parser.parse_args()))
    process.start()
