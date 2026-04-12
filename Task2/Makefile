.PHONY: all install generate scrape replace clean

ACTIVATE = source ../.venv/bin/activate

all: install generate scrape replace

install:
	$(ACTIVATE) && pip install -q -r requirements.txt

generate:
	$(ACTIVATE) && python3 generate_terms_map.py

scrape:
	$(ACTIVATE) && python3 scraper.py

replace:
	$(ACTIVATE) && python3 replace_terms.py

clean:
	rm -rf raw_data/ knowledge_base/
	rm -f terms_map.json
