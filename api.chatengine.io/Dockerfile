# Use an official Python runtime as a parent image, based on Alpine
FROM python:3.12.2

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT 8080

# Set the working directory and copy contents
WORKDIR /app
COPY . /app/

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Define the command to run uWSGI
CMD uwsgi --http :"${PORT}" --module server.wsgi

# Expose the port uWSGI will run on
EXPOSE ${PORT}