const uWS = require("uWebSockets.js");
const port = 9001;

function startServer() {
  uWS
    .App()
    .ws("/*", {
      /* WebSocket behavior */
      open: (ws) => {
        console.log("A WebSocket connected via URL: " + ws.url);
      },
      message: (ws, message, isBinary) => {
        /* Echo the message back */
        ws.send(message, isBinary);
      },
      close: (ws, code, message) => {
        console.log("WebSocket closed");
      },
    })
    .listen(port, (token) => {
      if (token) {
        console.log(`WebSocket server listening on port ${port}`);
      } else {
        console.log("Failed to listen on port " + port);
      }
    });
  return uWS;
}

module.exports = { startServer };
