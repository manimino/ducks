#!/bin/bash

pushd docs/
sphinx-apidoc ../filterbox -o .; make html
popd

