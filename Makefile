.PHONY: install run tasks verify clean test help

help:
	@echo "Sandbox System - Available Commands:"
	@echo ""
	@echo "  make install      - Install dependencies using uv pip"
	@echo "  make verify       - Verify all imports and connections"
	@echo "  make run          - Run interactive conversational agent"
	@echo "  make tasks        - Run predefined example tasks"
	@echo "  make map          - Show connection map of all modules"
	@echo "  make clean        - Clean up cache and temporary files"
	@echo "  make test         - Run tests (if available)"
	@echo "  make setup        - First-time setup (install + verify)"
	@echo "  make commit       - Stage and show status for commit"
	@echo "  make help         - Show this help message"
	@echo ""

install:
	@echo "Installing dependencies with uv pip..."
	uv pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

setup: install verify
	@echo ""
	@echo "✅ Setup complete! Next steps:"
	@echo "1. Add API keys to .env file"
	@echo "2. Run: make run"

verify:
	@echo "Verifying system..."
	python scripts/verify.py

run:
	@echo "Starting conversational agent..."
	python main.py

tasks:
	@echo "Running example tasks..."
	python main.py tasks

map:
	@echo "Generating connection map..."
	python scripts/map_connections.py

list-models:
	@echo "Listing available Gemini models..."
	python scripts/list_models.py

cleanup-sandboxes:
	@echo "Cleaning up all E2B sandboxes..."
	python scripts/cleanup_sandboxes.py

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build dist *.egg-info
	@echo "✅ Cleaned!"

test:
	@echo "Running tests..."
	@if [ -d "tests" ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "No tests directory found. Create tests/ to add tests."; \
	fi

commit:
	@echo "Staging changes..."
	git add -A
	@echo ""
	git status
	@echo ""
	@echo "Review changes above. To commit:"
	@echo "  git commit -m 'your message'"
	@echo "  git push"

check-env:
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found!"; \
		echo "Run: cp .env.example .env"; \
		echo "Then add your API keys."; \
		exit 1; \
	fi
	@echo "✅ .env file exists"

lint:
	@echo "Linting code..."
	@if command -v ruff > /dev/null; then \
		ruff check . ; \
	else \
		echo "ruff not installed. Install: uv pip install ruff"; \
	fi

format:
	@echo "Formatting code..."
	@if command -v ruff > /dev/null; then \
		ruff format . ; \
	else \
		echo "ruff not installed. Install: uv pip install ruff"; \
	fi
