import json

from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)


class WikiSpider(CrawlSpider):
    name = "wikiSpider"
    allowed_domains = ["jujutsu-kaisen.fandom.com"]
    start_urls = [
        "https://jujutsu-kaisen.fandom.com/api.php?"
        "action=query&list=categorymembers&cmtitle=Category:Characters&"
        "cmnamespace=0&cmlimit=5&format=json&formatversion=2"
    ]

    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 5,
        'CLOSESPIDER_PAGECOUNT': 5,
        'DOWNLOAD_DELAY': 1.5,
        'USER_AGENT': USER_AGENT,
        'ROBOTSTXT_OBEY': False,
    }

    rules = [
        Rule(
            LinkExtractor(
                allow=r'/wiki/',
                deny=(
                    r'/wiki/Category:', 
                    r'/wiki/File:', 
                    r'/wiki/Template:',
                    r'/wiki/User:',
                    r'/wiki/User_blog:',
                    r'/wiki/Special:',
                    r'/wiki/Forum:',
                    r'/wiki/Talk:',
                    r'\?action=',
                    r'\&oldid='
                )
            ),
            callback="parse_characters",
            follow=True
        )
    ]  

    def parse_start_url(self, response):
        data = json.loads(response.text)

        for page in data.get("query", {}).get("categorymembers", []):
            yield Request(
                url=(
                    "https://jujutsu-kaisen.fandom.com/api.php?"
                    f"action=parse&pageid={page['pageid']}&prop=text&"
                    "format=json&formatversion=2"
                ),
                callback=self.parse_api_page,
                headers={"User-Agent": USER_AGENT},
            )

    def parse_api_page(self, response):
        try:
            data = json.loads(response.text)
            html = data["parse"]["text"]
        except (KeyError, TypeError, ValueError):
            return

        page_title = data.get("parse", {}).get("title", "Unknown")
        page_response = HtmlResponse(
            url=f"https://jujutsu-kaisen.fandom.com/wiki/{page_title}",
            body=html.encode("utf-8"),
            encoding="utf-8",
            request=response.request,
        )
        yield from self.parse_characters(page_response)

    def parse_characters(self, response):
        infobox = response.css("aside.portable-infobox")
        if not infobox:
            return

        raw_name = response.css("h1#firstHeading::text").get()
        character_name = raw_name.strip() if raw_name else "Unknown"

        abilities = self.extract_section(response, "Jujutsu")
        if not abilities:
            abilities = self.extract_section(response, "Abilities_and_Powers")

        print(f"URL: {response.url}")
        yield {
            "character": character_name,
            "url": response.url,
            "raw_abilities": abilities
        }

    def parse_items(self, response):
        print(response.url)

    def extract_section(self, response, section):
        header = response.xpath(f"//h2[.//span[@id='{section}']]")
        if not header:
            return None

        content = []
        for sibling in header[0].xpath("following-sibling::*"):
            if sibling.root.tag == "h2":
                break

            if sibling.root.tag in ["p", "ul", "ol", "table"]:
                sibling_text = " ".join(sibling.xpath(".//text()").getall()).strip()
                if sibling_text:
                    content.append(sibling_text)
        return " ".join(content)
