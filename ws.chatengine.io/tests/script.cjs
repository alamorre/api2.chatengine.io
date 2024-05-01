const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/person"; // Adjust the URL as needed
const options = {
  headers: {
    "project-id": "c5394dc3-a877-4125-ace1-4baed7a98447",
    "user-name": "adam",
    "user-secret": "pass1234",
  },
};

// Connect to the WebSocket server
const ws = new WebSocket(wsUrl, options);

ws.on("open", function open() {
  console.log("Connection successfully opened");
  setTimeout(() => {
    ws.send('{"message":"Hello, world!"}');
  }, 500);
  setTimeout(() => {
    ws.close();
  }, 500);
});

ws.on("message", function incoming(data) {
  console.log("Received:", data.toString("utf8"));
});

ws.on("close", function close() {
  console.log("Connection closed");
});

ws.on("error", function error(err) {
  console.error("Connection error:", err.message);
});
