VERSION = 0.0.1

PYTHON := /usr/local/bin/python3.6
PIP := /usr/local/bin/pip3.6
BUILD_PATH := ./build
SOURCE_PATH := ./src

VENV_PATH := $(BUILD_PATH)/venv
WHEEL_PATH := $(BUILD_PATH)/wheels
REQUIREMENTS_FILE := $(BUILD_PATH)/requirements.txt
WHEELS_FILE := $(BUILD_PATH)/wheels.txt
SOURCES := $(shell find $(SOURCE_PATH) -name '*.py')
PACKAGE_FILE := $(BUILD_PATH)/wheels/putsync2-$(VERSION)-py2.py3-none-any.whl
PEX_FILE := $(BUILD_PATH)/putsync2.pex

.PHONY: all
	echo "None"

$(REQUIREMENTS_FILE): dependencies
	@echo "=========== Building virtualenvironment and requirements.txt"
	@virtualenv --python=$(PYTHON) $(VENV_PATH)
	@/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install -r dependencies && pip freeze >$(REQUIREMENTS_FILE)"
	@ln -sf $(VENV_PATH)/bin/activate activate

$(PACKAGE_FILE): $(SOURCES)
	@echo "=========== Packaging project"
	@$(PIP) wheel --wheel-dir=$(WHEEL_PATH) .

$(WHEELS_FILE): $(REQUIREMENTS_FILE)
	@echo "=========== Building dependent wheels"
	@$(PIP) wheel --wheel-dir=$(WHEEL_PATH) -r $(REQUIREMENTS_FILE)
	@cp $(REQUIREMENTS_FILE) $(WHEELS_FILE)

$(PEX_FILE): $(WHEELS_FILE) $(PACKAGE_FILE)
	@echo "=========== Building packaged PEX"
	@pex --no-index --disable-cache --python=$(PYTHON) -f $(BUILD_PATH)/wheels -o $(BUILD_PATH)/putsync2.pex --entry-point='putsync2.main:main' -r $(REQUIREMENTS_FILE) putsync2


all: $(PEX_FILE)

clean:
	rm -rf $(BUILD_PATH) activate
	find $(SOURCE_PATH) -type d -name '__pycache__' -exec rm -rf '{}' \;
	find $(SOURCE_PATH) -type f -name '*.pyc' -delete
