venv:
	python3 -m venv venv; \
	. venv/bin/activate; \
	pip install -r requirements.txt

install: venv

.PHONY: update
update:
	. venv/bin/activate; \
	pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
