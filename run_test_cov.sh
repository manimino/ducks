#!/bin/bash
# Generate a fresh coverage report. Requires pytest-cov.
pytest --cov-report term --cov=dbox test/ | tee test/cov.txt

