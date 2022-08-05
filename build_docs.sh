#!/bin/bash

pushd docs/
sphinx-apidoc ../hashbox -o source; make html
popd

