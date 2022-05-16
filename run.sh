#!/usr/bin/env bash
xvfb-run --server-args='-screen 0 1920x1080x24' python ./run.py $@
