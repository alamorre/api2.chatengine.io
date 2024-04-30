const WebSocket = require("ws");

// Define the WebSocket URL and any desired headers
const wsUrl = "ws://localhost:9001/person"; // Adjust the URL as needed
const options = {
  headers: {
    "public-key": "abc",
    username: "adam",
    secret: "pass1234",
  },
};

// Connect to the WebSocket server
const ws = new WebSocket(wsUrl, options);

ws.on("open", function open() {
  console.log("Connection successfully opened");
  // You can send a message or simply close the connection here
  ws.close();
});

ws.on("message", function incoming(data) {
  console.log("Received:", data);
});

ws.on("close", function close() {
  console.log("Connection closed");
});

ws.on("error", function error(err) {
  console.error("Connection error:", err.message);
});
