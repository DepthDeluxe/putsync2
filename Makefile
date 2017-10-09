VERSION = 0.0.1

PYTHON ?= python3.6
PIP ?= pip3.6
MAKE ?= make

BUILD_PATH := ./build
SOURCE_PATH := ./putsync2

VENV_PATH := $(BUILD_PATH)/venv
WHEEL_PATH := $(BUILD_PATH)/wheels
REQUIREMENTS_FILE := $(BUILD_PATH)/requirements.txt
SOURCES := $(shell find $(SOURCE_PATH) -name '*.py')
PACKAGE_FILE := $(BUILD_PATH)/wheels/putsync2-$(VERSION)-py2.py3-none-any.whl
PEX_FILE := $(BUILD_PATH)/putsync2.pex

.PHONY: all
	echo "None"

all: pex frontend

pex: $(PEX_FILE)


$(REQUIREMENTS_FILE): setup.py
	$(PYTHON) -m venv $(VENV_PATH)
	/bin/bash -c "source $(VENV_PATH)/bin/activate && pip install pex wheel && python setup.py develop && pip freeze -l | grep -v putsync > $(REQUIREMENTS_FILE) && pip wheel -r $(REQUIREMENTS_FILE) -w $(WHEEL_PATH)"


$(PACKAGE_FILE): $(SOURCES)
	/bin/bash -c "source $(VENV_PATH)/bin/activate && python setup.py bdist_wheel -d $(WHEEL_PATH)"


$(PEX_FILE): $(REQUIREMENTS_FILE) $(PACKAGE_FILE)
	/bin/bash -c "source $(VENV_PATH)/bin/activate && pex --no-index -f $(WHEEL_PATH) -o $(PEX_FILE) putsync2 -m putsync2"


frontend:
	cd ./putsync2-fe && $(MAKE)
	ln -s ../putsync2-fe/build/dist ./build/dist


clean:
	rm -rf $(BUILD_PATH) activate
	rm -rf *.egg-info
	cd ./putsync2-fe && $(MAKE) clean
	find $(SOURCE_PATH) -type d -name '__pycache__' -exec rm -rf '{}' \; || true
	find $(SOURCE_PATH) -type f -name '*.pyc' -delete || true
