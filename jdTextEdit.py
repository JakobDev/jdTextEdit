#!/usr/bin/env python3
from jdTextEdit.jdTextEdit import main
import traceback
import sys

try:
    main()
except Exception as e:
    print(traceback.format_exc(), end="", file=sys.stderr)