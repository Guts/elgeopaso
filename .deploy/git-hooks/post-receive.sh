#!/bin/sh

# Variables
# --------------------------------------------------------

# Folder where to deploy the application
WWW="/var/www/elgeopaso"

# A temporary directory for deployment
TMP="/srv/tmp/elgeopaso"

# The Git local repository
GIT="/srv/git/elgeopaso.git"

# Folder where to store environment files
ENV="/srv/env/elgeopaso"

# Operations
# --------------------------------------------------------

# Deploy the content to the temporary directory
mkdir -p \$TMP
git --work-tree=$TMP --git-dir=$GIT checkout -f

# Copy the env variable to the temporary directory
cp -a \$ENV/. \$TMP

# Build tasks
cd $TMP

# Replace the production directory content with the temporary content
cd /
rm -rf $WWW
mv $TMP $WWW

# Release tasks in production folder (start services, etc.)
cd \$WWW

# Create virtualenv and update pip
virtualenv -p /usr/bin/python3.7 .venv
source ./.venv/bin/activate
python -m pip install -U pip

# Install dependencies
python -m pip install -U -r requirements/production.txt
python -m nltk.downloader punkt stopwords

# Run migrations
python manage.py migrate
