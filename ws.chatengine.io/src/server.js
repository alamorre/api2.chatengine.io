const uWS = require("uWebSockets.js");
const port = 9001;

function startServer() {
  uWS
    .App()
    .ws("/*", {
      open: (ws) => {},
      message: (ws, message, isBinary) => {
        ws.send(message, false);
      },
      close: (ws, code, message) => {},
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
