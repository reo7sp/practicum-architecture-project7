.PHONY: all install test clean

ACTIVATE = source ../.venv/bin/activate

all: install test

install:
	$(ACTIVATE) && pip install -q -r requirements.txt

test:
	$(ACTIVATE) && pytest test_evaluate.py -v

clean:
	rm -f logs/logs.jsonl
