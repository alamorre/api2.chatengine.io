const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/ws/person/"; // Adjust the URL as needed
const options = {
  headers: {
    "private-key": "6d3b85b2-ffff-427f-86e0-76c41f6cd5ec",
    "user-name": "adam",
    "user-secret": "pass1234",
  },
};

// Connect to the WebSocket server
const ws = new WebSocket(wsUrl, options);

ws.on("open", function open() {
  console.log("Connection successfully opened");
});

ws.on("close", function close() {
  console.log("Connection closed");
});

ws.on("error", function error(err) {
  console.error("Connection error:", err.message);
});

// Output:
// Connection error: unexpected server response (401)
// Connection closed
