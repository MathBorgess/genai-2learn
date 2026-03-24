.PHONY: up down logs test clean build restart health

up:
	docker-compose up --build -d

down:
	docker-compose down

build:
	docker-compose build

restart:
	docker-compose restart

logs:
	docker-compose logs -f

health:
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@curl -s http://localhost:8001/health | python3 -m json.tool
	@curl -s http://localhost:8002/health | python3 -m json.tool

test:
	cd services/api-gateway && python -m pytest tests/ -v --tb=short
	cd services/workout-command && python -m pytest tests/ -v --tb=short
	cd services/effort-intelligence && python -m pytest tests/ -v --tb=short
	cd services/worker && python -m pytest tests/ -v --tb=short

test-cov:
	cd services/api-gateway && python -m pytest tests/ -v --cov=src --cov-report=term-missing
	cd services/workout-command && python -m pytest tests/ -v --cov=src --cov-report=term-missing
	cd services/effort-intelligence && python -m pytest tests/ -v --cov=src --cov-report=term-missing
	cd services/worker && python -m pytest tests/ -v --cov=src --cov-report=term-missing

clean:
	docker-compose down -v --remove-orphans

install-test-deps:
	pip install pytest pytest-cov
	cd services/api-gateway && pip install -r requirements.txt
	cd services/workout-command && pip install -r requirements.txt
	cd services/effort-intelligence && pip install -r requirements.txt
	cd services/worker && pip install -r requirements.txt
