.PHONY: install build

all: .PHONY

install: package.json
	@echo "====== Installing NPM Dependencies"
	@npm install

build:
	@echo "====== Building putsync2-fe"
	@npm run build

clean:
	@rm -rf build/dist node_modules
