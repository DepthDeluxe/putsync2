import logging
import time

from .core import db
from .core.configuration import Config
from .core.processor import ProcessorThread
from .core.scanner import ScannerThread
from .webapp import app

logger = logging.getLogger(__name__)

ProcessorThread().start()
ScannerThread().start()
app.run(port=9000)
