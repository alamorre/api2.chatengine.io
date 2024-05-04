const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/ws/person/"; // Adjust the URL as needed
const options = {
  headers: {
    "private-key": "6d3b85b2-000a-427f-86e0-76c41f6cd5ec",
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

// Output:
// Connection successfully opened
// Received: {"message":"Hello, world!"}
// Connection closed
