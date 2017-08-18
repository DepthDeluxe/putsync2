NPM ?= /opt/node-v8.4.0-linux-x64/bin/npm

.PHONY: install build

all: .PHONY

install: package.json
	@echo "====== Installing NPM Dependencies"
	@$(NPM) install

build:
	@echo "====== Building putsync2-fe"
	@ln -sf ../build
	@$(NPM) run build

clean:
	@rm -rf build/dist node_modules
