#!/bin/bash

pushd docs/
sphinx-apidoc ../dbox -o .; make html
popd

