# Use an official Python runtime as a parent image, based on Alpine
FROM python:3.12.2-alpine

# Set environment variables to ensure Python runs in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Set the port environment variable
ENV PORT 8080

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Upgrade pip
RUN pip install --upgrade pip

# Install system dependencies required for building uWSGI
RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers

# Install Python dependencies
RUN pip install -r requirements.txt

# Remove build dependencies to reduce image size
RUN apk del .build-deps

# Define the command to run uWSGI
CMD uwsgi --http :"${PORT}" --module server.wsgi

# Expose the port uWSGI will run on
EXPOSE ${PORT}