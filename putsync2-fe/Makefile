NPM ?= npm

.PHONY: install build

all: .PHONY

install: package.json
	@echo "====== Installing NPM Dependencies"
	@$(NPM) install

build:
	@echo "====== Building putsync2-fe"
	@mkdir -p build
	@NODE_ENV=production $(NPM) run build

clean:
	@rm -rf build node_modules
