FROM python:3.12.2-alpine
ENV PYTHONBUFFERED=1
ENV PORT 80
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD daphne -b 0.0.0.0 -p "${PORT}" server.asgi:application
EXPOSE ${PORT}