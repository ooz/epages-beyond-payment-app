FROM python:3-slim

LABEL maintainer="oliverzscheyge@gmail.com"

# Prevent apt from querying for a keyboard configuration
ENV DEBIAN_FRONTEND noninteractive

RUN pip install pipenv

# Copy order app files
COPY static /static
COPY templates /templates
COPY *.py /
COPY Pipfile* /

# Install dependencies
RUN pipenv install

EXPOSE 8080

# Hack to bind to correct IP/port for docker and use defaults for Heroku
ENV RUNNING_IN_DOCKER true

# Run app
CMD pipenv run python /app.py
