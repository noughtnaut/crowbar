#!/usr/bin/env bash
# Take a snapshot of what is currently defined as necessary for the project and store it in a file for
# future thawing. This means we don't need to store the VENV contents (which would be The Wrong Thing
# To Do, anyway).

pip freeze > requirements.txt
