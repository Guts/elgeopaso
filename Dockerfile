FROM python:3.10-slim-bookworm
LABEL MAINTAINER="Yves Jacolin"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade distrib
RUN apt update \
  # dependencies for building Python packages
  && apt install -y build-essential \
  # psycopg2 dependencies
  && apt install -y libpq-dev musl-dev \
  # Translations dependencies
  && apt install -y gettext \
  # cleaning up unused files
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Application requirements
COPY ./requirements /requirements
RUN python -m pip install --upgrade pip \
  && python -m pip install -r /requirements/production.txt \
  && python -m nltk.downloader punkt stopwords \
  && python -m pip install pyopenssl --upgrade

# Add release script
COPY .deploy/release-tasks.sh /release-tasks.sh
RUN sed -i 's/\r$//g' /release-tasks.sh \
  && chmod +x /release-tasks.sh

# Add entrypoint script
COPY ./.deploy/docker/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh \
  && chmod +x /entrypoint.sh

COPY ./ /app
# Move application files after requirements
WORKDIR /app
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
