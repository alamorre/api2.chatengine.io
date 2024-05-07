const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/ws/chat/"; // Adjust the URL as needed
const options = {
  headers: {
    "project-id": "c5394dc3-a877-4125-ace1-4baed7a98447",
    "chat-id": "1",
    "access-key": "ca-5573dea9-d7f1-4959-944e-267b8ce93935",
  },
};
// Connect to the WebSocket server
const ws = new WebSocket(wsUrl, options);

ws.on("open", function open() {
  console.log("Connection successfully opened");
});

ws.on("message", function incoming(data) {
  console.log("Received:", data.toString("utf8"));
});

ws.on("error", function error(err) {
  console.error("WebSocket encountered an error:", err);
});
