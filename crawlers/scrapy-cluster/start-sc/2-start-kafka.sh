#!/bin/bash

tmux new-session -s kafka "bash --init-file setup-kafka.sh"