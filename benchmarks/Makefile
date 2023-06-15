# Environment
PY := python3
GO := GO111MODULE=on go

#  Disable implicit rules
MAKEFLAGS += rR

## General:

.PHONY: all .FORCE
all: help
.FORCE: ;
Makefile: ;

define check_sys
	@if [[ $$(ulimit -n) -lt 4096 ]]; then\
        echo "The file descriptor limit seems low ($$(ulimit -n)). You might want to bump it with 'ulimit -n 4096'";\
    fi
	@if [[ $$(sysctl -w kern.ipc.somaxconn | cut -d ' ' -f 2) -lt 4096 ]]; then\
        echo "SOMAXCONN seems low ($$(sysctl -w kern.ipc.somaxconn | cut -d ' ' -f 2)). You might want to bump it with 'sudo sysctl -w kern.ipc.somaxconn=4096'";\
    fi
endef

.PHONY: install
install: ## Install all the dependencies needed for the benchmarks
	$(PY) -m pip install -r requirements.txt

.PHONY: run
run: ## Run all the benchmarks
	$(GO) run benchmark-runner

%:: .FORCE ## Run the specified benchmark
	$(call check_sys)
	$(GO) run benchmark-runner $@
	$(call check_sys)


## Help:

.PHONY: help
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