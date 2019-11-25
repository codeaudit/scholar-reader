FROM ubuntu:bionic

RUN apt-get update

# Install LaTeX suite
# This download will take an extremely long time to install, so we install it first
# Set DEBIAN_FRONTEND to disable tzdatainteractive dialogue
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y texlive-full

# Install Perl
# Build-essential is required for installing Perl dependencies
RUN apt-get install -y build-essential
# Old version (e.g., 5.22) needed to support TeX::AutoTeX
# Perl installation will take a very long time.
RUN apt-get install -y curl
RUN cpan App::perlbrew \
  && perlbrew init \
  && perlbrew install perl-5.22.4 \
  && perlbrew install-cpanm

# Install Postgres
RUN apt-get install -y postgresql

# Install Python
RUN apt-get install -y python3.7
RUN apt-get install -y python3-distutils
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py --force-reinstall

# Install Node.js
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt-get install -y nodejs

# Let ImageMagick to read and write PDFs
RUN sed -i '/pattern="PDF"/s/rights="none"/rights="read | write"/' /etc/ImageMagick-6/policy.xml

# Install pip requireements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install Perl dependencies
SHELL ["/bin/bash", "-c"]
RUN source ~/perl5/perlbrew/etc/bashrc \
  && perlbrew use perl-5.22.4 \
  && cpanm TeX::AutoTeX

# Install Node.js dependencies
WORKDIR /data-processing/node
RUN apt-get install -y git
COPY node/package*.json ./
RUN npm install
# As KaTeX is undegoing rapid changes, install it from sources
RUN npm install -g yarn
RUN npm run prepare-katex
RUN npm run install-katex

# Install vim for when we inevitably want to inspect files
RUN apt-get install -y vim

# Copy over the source code
WORKDIR /data-processing
COPY . .

# Set default Python to Python 3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Set up path to include Python scripts
ENV PYTHONPATH="/data-processing"