#!/bin/bash

# The production directory
WWW="/var/www/elgeopaso"

# A temporary directory for deployment
TMP="/srv/tmp/elgeopaso"

# The Git repo
GIT="/srv/git/elgeopaso.git"

# The Env  repo
ENV="/srv/env/elgeopaso"

# Deploy the content to the temporary directory
mkdir -p $TMP
git --work-tree=$TMP --git-dir=$GIT checkout -f

# Copy the env variable to the temporary directory
echo "GIT STEP - Copy '.env' file to the temp folder"
cp -a $ENV/. $TMP

# Build tasks
cd $TMP
# Remove useless files and folders
rm -rf ./vscode

# Replace the content of the production directory
# with the temporary directory
cd / || exit

echo "GIT STEP - Clean final folder: $WWW"
rm -rf $WWW

echo "GIT STEP - Move new file structure from $TMP to $WWW"
mv $TMP $WWW

# Release tasks
cd $WWW || exit

# Create virtualenv and update pip
virtualenv -p /usr/bin/python3.10 .venv
source ./.venv/bin/activate
python -m pip install -U pip setuptools wheel

# Install dependencies
python -m pip install -U -r requirements/production.txt
python -m nltk.downloader punkt punkt_tab stopwords

# Run migrations
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput
