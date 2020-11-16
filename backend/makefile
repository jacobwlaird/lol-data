typehint: 
	mypy resources/python/loldata.py

lint:
	pylint resources/python/loldata.py
	pylint resources/python/classes
	pylint resources/python/scripts

checklist: lint typehint
.PHONY: typehint lint
