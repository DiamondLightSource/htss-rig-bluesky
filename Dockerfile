# This file is for use as a devcontainer and a runtime container
#
# The devcontainer should use the build target and run as root with podman
# or docker with user namespaces.
#
FROM python:3.10 as build

ARG PIP_OPTIONS=.

# Install system dependencies
RUN apt update; \
    apt install ffmpeg libsm6 libxext6 libegl1 libqt5gui5 -y

# set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# Copy any required context for the pip install over
COPY . /context
WORKDIR /context

# install python package into /venv
RUN pip install ${PIP_OPTIONS}

FROM python:3.10-slim as runtime

# Install system dependencies
RUN apt update; \
    apt install ffmpeg libsm6 libxext6 libegl1 libqt5gui5 -y

# copy the virtual environment from the build stage and put it in PATH
COPY --from=build /venv/ /venv/
ENV PATH=/venv/bin:$PATH

# change this entrypoint if it is not the same as the repo
ENTRYPOINT ["htss"]
