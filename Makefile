PY=python3
PIP=python3 -m pip

OS:=$(shell uname)

all: help


## General:

install: ## Install the developement dependencies
	$(PIP) install -r requirements.txt

test: ## Run the tests with coverage
	$(PY) -m pytest --cov=nanohttpy

cover: ## Run the tests and open the html report in the browser
	$(PY) -m pytest --cov=nanohttpy --cov-report=term --cov-report=html
ifeq ($(OS),Darwin)
	open htmlcov/index.html
endif


## Help:

.SILENT: help
help: ## Show this help.
	# Self generating help
	# Inspired from https://gist.github.com/thomaspoignant/5b72d579bd5f311904d973652180c705#file-makefile-L89
	echo 'Usage:'
	echo '  make [target]...'
	echo ''
	echo 'Targets:'
	awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "        %-20s%s\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "\n    %s\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)
	echo ''
