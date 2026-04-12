.PHONY: all install build test clean

ACTIVATE = source ../.venv/bin/activate

all: install build test

install:
	$(ACTIVATE) && pip install -q -r requirements.txt

build:
	$(ACTIVATE) && python build_index.py

test:
	$(ACTIVATE) && python query_example.py

clean:
	rm -rf chroma_db/
