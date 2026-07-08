import os
import sys

if sys.platform != "win32":
    os.environ.setdefault("LOCALAPPDATA", "/tmp/fake-localappdata")
