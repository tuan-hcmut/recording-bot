# Use Python 3.10 as base image
FROM python:3.10

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Update pip
RUN pip install --no-cache-dir --upgrade pip

# Install Chrome and ChromeDriver dependencies
RUN apt-get update && apt-get install -y wget gnupg curl unzip

# Install some necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    pulseaudio \
    pavucontrol \
    sudo \
    pulseaudio \
    xvfb \
    libnss3-tools \
    ffmpeg \
    xdotool \
    x11vnc \
    libfontconfig \
    libfreetype6 \
    xfonts-scalable \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    xterm \
    vim

RUN usermod -aG audio root
RUN adduser root pulse-access

ENV key=value DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
ENV XDG_RUNTIME_DIR=/run/user/0


RUN mkdir -p /run/dbus
RUN chmod 755 /run/dbus

RUN rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse


RUN dbus-daemon --system --fork



RUN wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz

RUN tar -xvf pa_stable_v190700_20210406.tgz

RUN mv portaudio /usr/src/

WORKDIR /usr/src/portaudio

RUN ./configure && \
    make && \
    make install && \
    ldconfig

RUN echo 'user ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN adduser root pulse-access

RUN mkdir -p /var/run/dbus

RUN dbus-uuidgen > /var/lib/dbus/machine-id

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb -o chrome.deb
RUN dpkg -i chrome.deb || apt-get install -fy

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=114.0.5735.90; \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Clean up
RUN rm chrome.deb /tmp/chromedriver.zip

# Set working directory
WORKDIR /usr/src/app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

RUN touch /root/.Xauthority
RUN chmod 600 /root/.Xauthority
RUN chmod +x entrypoint.sh

RUN rm /run/dbus/pid
RUN mv pulseaudio.conf /etc/dbus-1/system.d/pulseaudio.conf

# Run the application
# CMD [ "./entrypoint.sh" ]