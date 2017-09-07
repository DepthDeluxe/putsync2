VERSION = 0.0.1

PYTHON ?= python3.6
PIP ?= pip3.6
MAKE ?= make

BUILD_PATH := ./build
SOURCE_PATH := ./putsync2

VENV_PATH := $(BUILD_PATH)/venv
WHEEL_PATH := $(BUILD_PATH)/wheels
REQUIREMENTS_FILE := $(BUILD_PATH)/requirements.txt
WHEELS_FILE := $(BUILD_PATH)/wheels.txt
SOURCES := $(shell find $(SOURCE_PATH) -name '*.py')
PACKAGE_FILE := $(BUILD_PATH)/wheels/putsync2-$(VERSION)-py2.py3-none-any.whl
PEX_FILE := $(BUILD_PATH)/putsync2.pex

.PHONY: all
	echo "None"

all: $(PEX_FILE) frontend

$(REQUIREMENTS_FILE): dependencies
	@echo "=========== Building virtualenvironment and requirements.txt"
	@$(PYTHON) -m venv $(VENV_PATH)
	@/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install -r dependencies && pip freeze >$(REQUIREMENTS_FILE)"
	@ln -sf $(VENV_PATH)/bin/activate activate

$(PACKAGE_FILE): $(SOURCES)
	@echo "=========== Packaging project"
	@/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install wheel && pip wheel --wheel-dir=$(WHEEL_PATH) ."

$(WHEELS_FILE): $(REQUIREMENTS_FILE)
	@echo "=========== Building dependent wheels"
	@/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install wheel && pip wheel -r $(REQUIREMENTS_FILE) --wheel-dir=$(WHEEL_PATH)"
	@cp $(REQUIREMENTS_FILE) $(WHEELS_FILE)

$(PEX_FILE): $(WHEELS_FILE) $(PACKAGE_FILE)
	@echo "=========== Building packaged PEX"
	@/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install pex && pex --no-index --disable-cache --python=$(PYTHON) -f $(BUILD_PATH)/wheels -o $(BUILD_PATH)/putsync2.pex --entry-point='putsync2.main:main' -r $(REQUIREMENTS_FILE) putsync2"

frontend:
	cd ./putsync2-fe && $(MAKE)
	ln -s ../putsync2-fe/build/dist ./build/dist

clean:
	rm -rf $(BUILD_PATH) activate
	cd ./putsync2-fe && $(MAKE) clean
	find $(SOURCE_PATH) -type d -name '__pycache__' -exec rm -rf '{}' \; || true
	find $(SOURCE_PATH) -type f -name '*.pyc' -delete || true
