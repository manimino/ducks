#!/bin/bash

pydoc-markdown -I . -m hashbox.mutable.main --render-toc > docs/HashBox.md
pydoc-markdown -I . -m hashbox.frozen.main --render-toc > docs/FrozenHashBox.md
