.PHONY: install test clean

VENV_DIR := .venv
PYTHON_VERSION ?= python3.13 # Default to python3.13, can be overridden (e.g., make install PYTHON_VERSION=python3.12)
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PYTEST := $(VENV_DIR)/bin/pytest

# Default target
all: test

# Create and activate virtual environment, then install dependencies
install: $(VENV_DIR)
	@echo "Installing Python dependencies using $(PYTHON_VERSION)..."
	$(PIP) install -r crawler/requirements.txt
	$(PIP) install -r crawler/requirements-dev.txt
	@echo "Python dependencies installed."

$(VENV_DIR):
	@echo "Creating virtual environment using $(PYTHON_VERSION)..."
	$(PYTHON_VERSION) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

# Run tests with coverage
test: install
	@echo "Running tests..."
	$(PYTEST) -c crawler/pytest.ini crawler/tests
	@echo "Tests finished."

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete."
