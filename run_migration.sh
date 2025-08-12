#!/bin/bash
export FLASK_APP=backend.app:app
/app/.venv/bin/python -m flask db stamp head
