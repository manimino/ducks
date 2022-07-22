#!/bin/bash
# Generate a fresh coverage report. Requires pytest-cov.
pytest --cov-report term --cov=hashindex test/ | tee test/cov.txt

