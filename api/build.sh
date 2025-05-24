#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install wheel first
pip install wheel

# Install mysql-connector-python explicitly first
pip install mysql-connector-python==8.3.0

# Install APScheduler explicitly
pip install APScheduler==3.10.4

# Install other dependencies
pip install -r requirements.txt 