# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

class AnimecrawlerPipeline:
    def process_item(self, item):
        raw_text = item.get("raw_abilities")
        if not raw_text:
            return item

        clean_text = re.sub(r"\[\s*\d+\s*\]", "", raw_text)
        clean_text = re.sub(r"\[(?:Edit|Expand|Collapse)\]", "", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\([^)]*[^\x00-\x7F][^)]*\)", "", clean_text)
        clean_text = re.sub(r"[^\x00-\x7F]", "", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text)

        item["raw_abilities"] = clean_text

        return item

        
