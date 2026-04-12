import requests
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path
from tqdm import tqdm

class StarWarsScraper:
    def __init__(self, output_dir='raw_data'):
        self.base_url = 'https://en.wikipedia.org/wiki/'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[\d+\]', '', text)
        text = text.strip()
        return text

    def scrape_article(self, article_name):
        url = f"{self.base_url}{article_name}"

        try:
            print(f"Scraping: {article_name}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.find('h1', {'id': 'firstHeading'})
            title_text = title.get_text(strip=True) if title else article_name.replace('_', ' ')

            content_div = soup.find('div', {'class': 'mw-parser-output'})
            if not content_div:
                print(f"  Warning: No content found for {article_name}")
                return None

            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 50:
                    paragraphs.append(self.clean_text(text))

            if not paragraphs:
                print(f"  Warning: No paragraphs found for {article_name}")
                return None

            document = f"# {title_text}\n\n" + "\n\n".join(paragraphs[:20])

            filename = f"{article_name.replace('/', '_')}.txt"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document)

            print(f"  Saved to {filename} ({len(paragraphs[:20])} paragraphs)")
            return document

        except requests.exceptions.RequestException as e:
            print(f"  Error scraping {article_name}: {e}")
            return None
        except Exception as e:
            print(f"  Unexpected error for {article_name}: {e}")
            return None

    def scrape_multiple(self, article_list, delay=1.0):
        results = {}

        for article in tqdm(article_list, desc="Scraping articles"):
            result = self.scrape_article(article)

            if result:
                results[article] = result

            time.sleep(delay)

        print(f"\nSuccessfully scraped {len(results)}/{len(article_list)} articles")
        return results


STAR_WARS_ARTICLES = [
    "Darth_Vader",
    "Luke_Skywalker",
    "Princess_Leia",
    "Han_Solo",
    "Obi-Wan_Kenobi",
    "Yoda",
    "Palpatine",
    "Anakin_Skywalker",
    "Rey_(Star_Wars)",
    "Kylo_Ren",
    "Darth_Maul",
    "Chewbacca",
    "C-3PO",
    "R2-D2",
    "Boba_Fett",
    "Padmé_Amidala",
    "Qui-Gon_Jinn",
    "Mace_Windu",
    "Count_Dooku",
    "General_Grievous",
    "Death_Star",
    "Lightsaber",
    "Millennium_Falcon",
    "TIE_fighter",
    "X-wing",
    "Star_Destroyer",
    "AT-AT",
    "Tatooine",
    "Coruscant",
    "Hoth",
    "Endor_(Star_Wars)",
    "Naboo",
    "Dagobah",
    "Alderaan",
    "Mustafar",
    "Bespin",
    "Jakku",
    "The_Force",
    "Jedi",
    "Sith",
    "Galactic_Empire_(Star_Wars)",
    "Rebel_Alliance",
    "First_Order_(Star_Wars)",
    "Galactic_Republic",
    "Wookiee",
    "Droid_(Star_Wars)",
    "Stormtrooper_(Star_Wars)",
    "Clone_trooper",
    "Mandalorian"
]


if __name__ == "__main__":
    scraper = StarWarsScraper()
    print("Starting Star Wars Wikipedia scraper...")
    print(f"Will scrape {len(STAR_WARS_ARTICLES)} articles\n")

    results = scraper.scrape_multiple(STAR_WARS_ARTICLES, delay=0.5)

    print(f"\n{'='*50}")
    print(f"Scraping complete! {len(results)} files saved to '{scraper.output_dir}'")
