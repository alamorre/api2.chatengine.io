const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/ws/chat/"; // Adjust the URL as needed
const options = {
  headers: {
    "chat-id": "1",
    "private-key": "6d3b85b2-ffff-427f-86e0-76c41f6cd5ec",
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
