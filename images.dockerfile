# Use a base image with Python 3.10 installed
FROM python:3.10-slim

# Set environment variable to prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=America/New_York
ENV PATH="${PATH}:/app"
ENV LANG=en_US.UTF-8 
ENV DEBUG=true
ENV APPLICATION_ENV=production
ENV TERM=xterm-256color
ENV SHELL=/bin/bash


# Install pipenv using pipx
RUN pip install --upgrade pipenv
RUN pip install --no-cache-dir pipx 

#RUN python -m pipx ensurepath
RUN  pipx install pipenv

# Create a non-root user to run the application
#RUN useradd -D -h /home/notificationbot -s /bim/sh notificationbot
#RUN useradd -m -s /bin/bash notificationbot

# Set the working directory inside the container
#WORKDIR /home/notificationbot/app
WORKDIR /app

# Switch to the non-root user
#USER notificationbot

#RUN mkdir -p /home/notificationbot/.local

#RUN chown -R notificationbot:notificationbot /home/notificationbot/app

#RUN chmod 775 /home/notificationbot/app

# Copy only the Pipfile and Pipfile.lock initially to leverage Docker layer caching
#COPY Pipfile Pipfile.lock /home/notificationbot/app/
COPY Pipfile Pipfile.lock /app/

#ENV PATH="${PATH}:/home/notificationbot/.local/"

# Install dependencies using pipenv
RUN pipenv install --deploy --system --ignore-pipfile
RUN pipenv sync
RUN pipenv graph

# Copy the rest of the application code
#COPY . /home/notificationbot/app/
COPY . /app

# Copy secrets file into the container
#COPY secrets.json /home/notificationbot/app/secrets.json
COPY secrets.json app/secrets.json

# Adjust permissions of the secrets file
#RUN chmod 600 /home/notificationbot/app/secrets.json
RUN chmod 600 app/secrets.json

# Create a directory for logs
#RUN mkdir /home/notificationbot/app/log
RUN mkdir /app/log

# Copy the log files into the logs directory
COPY discord.log twitch.log /home/notificationbot/app/log/
COPY discord.log twitch.log app/log/

# Switch to the non-root user
#USER notificationbot

# Command to run the Python application using pipenv
CMD ["pipenv", "run", "python", "discordbot.py"]
