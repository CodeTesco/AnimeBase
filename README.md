# 呪術廻戦 AnimeBase

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.11+-orange.svg?logo=scrapy&logoColor=white)](https://scrapy.org)
[![Format](https://img.shields.io/badge/Output-JSONLines-000000.svg?logo=json&logoColor=white)](#)

An end-to-end data engineering pipeline designed to convert unstructured, deeply nested wiki lore into a clean, machine-readable corpus. It specifically targets the Jujutsu Kaisen power system (Cursed Energy, Innate Techniques, Domain Expansions), extracting data via the MediaWiki API and passing it through a strict Regex cleaning pipeline to generate LLM-ready `.jsonl` files.

## 🏗️ Architecture & Data Flow

```text
[ Fandom MediaWiki API ]
        │
        ├──> (1) Category Pagination ──> Extracts page IDs via `cmcontinue` tokens
        │
        ├──> (2) Payload Parser      ──> Reconstructs raw JSON payloads into Scrapy `HtmlResponse` objects
        │
        ├──> (3) DOM Extraction      ──> Isolates `<aside>` infoboxes and targeted `<h2>` DOM siblings
        │
        ├──> (4) Regex Pipeline      ──> Strips citations, UI artifacts, and Romaji phonetic text
        │
        └──> (5) JSONL Exporter      ──> Appends clean, independent JSON objects to `jjk_characters.jsonl`
```

## ⚡ Engineering Challenges Solved

### 1. Bypassing Fandom HTML Bloat
Standard web scraping on Fandom triggers massive overhead from ads and JavaScript tabs.
* **Solution:** Bypassed the frontend entirely by querying the MediaWiki API directly (`action=parse&prop=text`). Reconstructed the JSON payload back into Scrapy `HtmlResponse` objects in-memory to utilize standard XPath/CSS selectors on the pure text payload.

### 2. Defeating API Pagination Limits
MediaWiki forcibly caps queries at 500 items per request, masking the true size of the wiki.
* **Solution:** Implemented a recursive callback loop that reads `cmcontinue` continuation tokens from the API response and automatically yields newly constructed Requests until the entire character category is exhausted.

### 3. NLP Text Sanitization
Feeding raw wiki text to an LLM causes severe hallucination due to embedded UI artifacts (`[Edit]`, `[Expand]`), citation brackets (`[1]`), and redundant phonetic Japanese strings.
* **Solution:** Built a Scrapy Item Pipeline that applies sequential Regex passes to obliterate non-contextual noise and normalize whitespace before the data ever touches the disk.

## 📄 Output Schema Example (`.jsonl`)
The pipeline outputs strict JSONLines, perfect for direct ingestion into HuggingFace Datasets or Vector Databases (Pinecone, ChromaDB).

```json
{"character": "Satoru Gojo", "url": "[https://jujutsu-kaisen.fandom.com/wiki/Satoru_Gojo](https://jujutsu-kaisen.fandom.com/wiki/Satoru_Gojo)", "raw_abilities": "Satoru is the pride of the Gojo Family, the first person to inherit both the Limitless and the Six Eyes in four hundred years..."}
{"character": "Ryomen Sukuna", "url": "[https://jujutsu-kaisen.fandom.com/wiki/Ryomen_Sukuna](https://jujutsu-kaisen.fandom.com/wiki/Ryomen_Sukuna)", "raw_abilities": "Sukuna possesses immense levels of cursed energy due to his innate power, cementing his title as the King of Curses..."}
```

## 📜 License
* **Code:** MIT
* **Data:** The underlying extracted lore is property of Gege Akutami and SHUEISHA Inc.