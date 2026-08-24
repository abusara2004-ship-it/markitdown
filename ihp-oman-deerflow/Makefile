.PHONY: help setup install clean test run dev verify

# Colors
BLUE=\033[0;34m
GREEN=\033[0;32m
NC=\033[0m

help:
	@echo "$(BLUE)IHP Oman DeerFlow - Available Commands$(NC)"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup      - Run Phase 1 setup (directories, venv, dependencies)"
	@echo "  make install    - Install Python dependencies"
	@echo "  make clean      - Remove temporary files and caches"
	@echo ""
	@echo "Verification & Testing:"
	@echo "  make verify     - Verify Phase 1 setup is complete"
	@echo "  make test       - Run test suite"
	@echo "  make lint       - Run code linting (flake8)"
	@echo ""
	@echo "Database:"
	@echo "  make init-db    - Initialize database"
	@echo "  make reset-db   - Reset database (WARNING: deletes data)"
	@echo ""
	@echo "Development:"
	@echo "  make dev        - Start DeerFlow in development mode"
	@echo "  make run        - Run system (production mode)"
	@echo "  make logs       - Tail application logs"
	@echo ""

setup:
	@echo "$(BLUE)[Phase 1] Running setup...$(NC)"
	@bash scripts/setup_phase1.sh

install:
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

verify:
	@echo "$(BLUE)Verifying setup...$(NC)"
	python3 scripts/verify_setup.py

test:
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v --cov=agents --cov=skills --cov=integrations

lint:
	@echo "$(BLUE)Running linter...$(NC)"
	flake8 agents/ skills/ integrations/ --max-line-length=100

init-db:
	@echo "$(BLUE)Initializing database...$(NC)"
	python3 scripts/init_db.py

reset-db:
	@echo "$(BLUE)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (type 'yes'): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f .deer-flow/ihp_oman.db; \
		echo "$(BLUE)Database file deleted. Run 'make init-db' to reinitialize.$(NC)"; \
	else \
		echo "Cancelled."; \
	fi

dev:
	@echo "$(BLUE)Starting DeerFlow (development mode)...$(NC)"
	source venv/bin/activate && \
	export DEERFLOW_MODE=development && \
	export DEBUG_MODE=true && \
	deerflow dev

run:
	@echo "$(BLUE)Starting DeerFlow (production mode)...$(NC)"
	source venv/bin/activate && \
	export DEERFLOW_MODE=production && \
	deerflow up

logs:
	@echo "$(BLUE)Tailing application logs...$(NC)"
	tail -f .deer-flow/logs/agent.log

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name '*.egg-info' -delete
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.DEFAULT_GOAL := help
