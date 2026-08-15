PYTHON ?= python3

.PHONY: install generate-data generate-contracts validate test api demo-up demo-down create-topics bootstrap zip

install:
	$(PYTHON) -m pip install -r requirements.txt

generate-data:
	$(PYTHON) scripts/generate_merchants.py --output data/merchants.csv
	$(PYTHON) scripts/produce_trip_events.py --events-output data/sample_trip_events.jsonl --state-output data/sample_trip_state.jsonl --kafka-output data/sample_trip_events.kafka.txt --state-kafka-output data/sample_trip_state.kafka.txt

generate-contracts:
	$(PYTHON) scripts/generate_contracts.py

validate:
	$(PYTHON) scripts/validate_repo.py

test:
	pytest -q

api:
	uvicorn app.main:app --reload --port 8010

demo-up:
	docker compose up -d

demo-down:
	docker compose down -v

create-topics:
	bash scripts/create_topics.sh

bootstrap:
	bash scripts/bootstrap_demo.sh

zip:
	cd .. && zip -qr apache-pinot-bible.zip apache-pinot-bible
