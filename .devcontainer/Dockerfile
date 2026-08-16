# Workshop devcontainer: everything needed to write and test Ansible modules.
# Deliberately pinned so every attendee gets the same toolchain.
FROM python:3.12-slim

# ansible-test's integration runner and general dev ergonomics need these.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        make \
        vim \
        less \
        ca-certificates \
        rsync \
    && rm -rf /var/lib/apt/lists/*

# Pin the toolchain. ansible-core (not the big "ansible" package) is what module
# authors develop against; it ships ansible-test.
RUN pip install --no-cache-dir \
        "ansible-core>=2.16,<2.18" \
        "pytest>=8.0" \
        "pytest-mock>=3.12" \
        "pyyaml>=6.0"

# A non-root user is nicer for VS Code and avoids root-owned files on bind mounts.
ARG USERNAME=workshop
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME
WORKDIR /workshop

# Handy default so `python module.py args.json` works and imports resolve.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD ["bash"]
