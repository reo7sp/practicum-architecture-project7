.PHONY: install console telegram

ACTIVATE = source ../.venv/bin/activate

all: install console

install:
	$(ACTIVATE) && pip install -q -r requirements.txt

console:
	$(ACTIVATE) && python console_bot.py

telegram:
	$(ACTIVATE) && python telegram_bot.py
