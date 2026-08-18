#!/usr/bin/env python3
import sys
from scripts.setup_db import setup_database

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
