FROM debian:trixie-slim

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install dependencies for building radare2
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Clone radare2 source in its own layer
RUN git clone https://github.com/radareorg/radare2.git /opt/radare2

# 3. Install radare2 in its own layer
RUN /opt/radare2/sys/install.sh

# 4. Install the other tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdb \
    nasm \
    gcc \
    hexedit \
    wget \
    curl \
    man-db \
    unzip \
    file \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Wine for running Windows binaries
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    wine \
    wine32 \
    wine64 \
    && rm -rf /var/lib/apt/lists/*

# 6. Install Python and create a virtual environment
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && \
    python3 -m venv /opt/venv && \
    rm -rf /var/lib/apt/lists/*

# 7. Add venv to PATH and install packages
ENV PATH="/opt/venv/bin:$PATH"
COPY crawler/requirements.txt /tmp/requirements.txt
COPY crawler/requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install uv && \
    uv pip install -r /tmp/requirements.txt && \
    uv pip install -r /tmp/requirements-dev.txt

# 8. Create user and home directory
RUN useradd -ms /bin/bash -d /home/user user

# 9. Copy crawler source and set up command
COPY crawler /home/user/crawler
RUN chown -R user:user /home/user/crawler && \
    chmod +x /home/user/crawler/crawler.py && \
    ln -s /home/user/crawler/crawler.py /opt/venv/bin/get-crackme

# 10. Switch to non-root user
USER user
WORKDIR /home/user

# Set up a volume for the crackmes, so you can work from your host machine
VOLUME /home/user/crackmes

# Start a bash shell by default
CMD ["/bin/bash"]
