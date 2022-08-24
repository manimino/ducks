#!/bin/bash
# Generate a fresh coverage report. Requires pytest-cov.
pytest --cov-report term --cov=filterbox test/ | tee test/cov.txt

