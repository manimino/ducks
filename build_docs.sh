#!/bin/bash

pushd docs/
sphinx-apidoc ../ducks -o .; make html
popd

