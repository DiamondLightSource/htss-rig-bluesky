# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
ARG PYTHON_VERSION=3.11@sha256:6f4ad35576ea868518b5621c31595bf5a56b9b0c333f18118c868543c7f7cf40
FROM python:${PYTHON_VERSION} AS developer

# Add any system dependencies for the developer/build environment here
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    ffmpeg \
    libsm6 \
    libxext6 \
    libegl1 \
    libqt5gui5 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# The build stage installs the context into the venv
FROM developer AS build
# Requires buildkit 0.17.0
COPY --chmod=o+wrX . /workspaces/htss-rig-bluesky
WORKDIR /workspaces/htss-rig-bluesky
RUN touch dev-requirements.txt && pip install -c dev-requirements.txt .


# The runtime stage copies the built venv into a slim runtime container
FROM python:${PYTHON_VERSION}-slim AS runtime
# Add apt-get system dependecies for runtime here if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libegl1 \
    libqt5gui5 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /venv/ /venv/
ENV PATH=/venv/bin:$PATH

# change this entrypoint if it is not the same as the repo
ENTRYPOINT ["htss"]
CMD ["--version"]
