from bs4 import BeautifulSoup
import requests
import json
from pathlib import Path

root_path = Path(__file__).parents[2].resolve()
print(root_path)
output_path = root_path / "data" / "helper_data" / "slick_category.json"

url = "https://slickdeals.net/deal-categories/"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, "lxml")

all_categories = []

def extract_categories(ul):
    for li in ul.find_all("li", recursive=False):
        a_tag = li.find("a")
        if a_tag and a_tag.get("href"):
            category_slug = a_tag["href"].rstrip("/").split("/")[-1]
            all_categories.append(category_slug)

        nested_ul = li.find("ul")
        if nested_ul:
            extract_categories(nested_ul)

root_ul = soup.select_one(".content-box.all-categories ul")
extract_categories(root_ul)

# Save scraped categories
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_categories, f, indent=2)

print(f"Saved {len(all_categories)} categories → {output_path}")
