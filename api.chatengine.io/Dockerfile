# Use an official Python runtime as a parent image, based on Alpine
FROM cgr.dev/chainguard/python:latest-dev

# Switch to root user to install packages
USER root

# Install dependencies and time zone data
RUN apk update && apk add --no-cache tzdata

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT 8080
ENV TZ=UTC

# Switch back to non-root user
USER nonroot

# Set the working directory and copy contents
WORKDIR /app
COPY . /app/

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run as a python module
ENTRYPOINT ["python"]
CMD ["-m", "gunicorn", "-b", "0.0.0.0:8080", "server.wsgi:application"]
EXPOSE ${PORT}