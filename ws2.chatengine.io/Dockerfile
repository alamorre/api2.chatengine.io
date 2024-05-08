FROM node:20.12.1-buster-slim

WORKDIR /usr/src/app

COPY . .

# Install production dependencies.
RUN npm install --only=production

# Expose the port the app runs on
EXPOSE 9001

# Run the web service on container startup.
CMD [ "node", "src/main.js" ]
