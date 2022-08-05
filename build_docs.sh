#!/bin/bash

pushd docs/
sphinx-apidoc ../hashbox -o .; make html
popd

