const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/person"; // Adjust the URL as needed
const options = {
  headers: {
    "project-id": "c5394dc3-a877-4125-ace1-4baed7a98447",
    "user-name": "bad_user",
    "user-secret": "bad_pwd",
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
