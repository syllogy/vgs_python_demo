#!/usr/bin/env python
import argparse
from demo import app


_app = app.run_app()

if __name__ == "__main__":
  _app.run(host='0.0.0.0')
