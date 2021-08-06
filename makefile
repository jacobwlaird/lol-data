typehint: 
	mypy resources/python/loldata.py

lint:
	pylint resources/python/loldata.py
	pylint resources/python/classes
	pylint resources/python/scripts
	pylint resources/python/remove_last_data.py
	pylint resources/python/get_champ_card_data.py
	pylint resources/python/assert_db.py
	pylint resources/python/update_db_from_api.py

checklist: lint typehint
.PHONY: typehint lint
