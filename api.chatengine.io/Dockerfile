# Use the Chainguard Python dev image for build stage
FROM cgr.dev/chainguard/python:latest-dev as dev

# Switch to root user to install packages
USER root

# Set the working directory and copy contents
WORKDIR /app
COPY . /app/

# Install dependencies
RUN apk update && apk add --no-cache tzdata
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Switch back to non-root user
USER nonroot

# Final stage
FROM cgr.dev/chainguard/python:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT 8080
ENV TZ=UTC

# Set the working directory
WORKDIR /app

# Copy everything from the build image
COPY --from=dev /app /app/
COPY --from=dev /usr/share/zoneinfo /usr/share/zoneinfo

# Set the path for the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Run as a python module
ENTRYPOINT ["python"]
CMD ["-m", "gunicorn", "-b", "0.0.0.0:8080", "--workers", "3", "server.wsgi:application"]
EXPOSE ${PORT}
