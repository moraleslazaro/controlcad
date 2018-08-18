#!/usr/bin/env python
import os
import sys
from os import environ

# For compatibility outside portable shell environment.
# Very useful in PyCharm IDE.
if not 'BASE_DIR' in environ:
    environ['BASE_DIR'] = os.getcwd()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "controlcad.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
