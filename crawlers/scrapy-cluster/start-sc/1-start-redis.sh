#!/bin/bash

tmux new-session -s redis "bash --init-file setup-redis.sh"