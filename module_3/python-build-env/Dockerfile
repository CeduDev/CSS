ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION-slim-bullseye
COPY ./ /app/
WORKDIR /app
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential python-setuptools
RUN pip install pylint
RUN pip install pytest
RUN pip install nbmake
