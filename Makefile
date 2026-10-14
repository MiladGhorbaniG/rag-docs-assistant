.PHONY: install test lint eval up

install:
	python -m pip install -e "./backend[dev]"
	npm --prefix frontend install

test:
	cd backend && python -m pytest

lint:
	cd backend && ruff check . && ruff format --check .
	npm --prefix frontend run lint

eval:
	cd backend && python -m app.eval.run_eval

up:
	docker compose up --build
