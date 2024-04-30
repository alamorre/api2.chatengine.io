const uWS = require("uWebSockets.js");
const port = 9001;

function startServer() {
  let token; // This will hold the listen token

  const app = uWS
    .App()
    .ws("/*", {
      open: (ws) => {
        console.log("A WebSocket connected");
      },
      message: (ws, message, isBinary) => {
        ws.send(message, isBinary);
      },
      close: (ws, code, message) => {
        console.log("WebSocket closed");
      },
    })
    .listen(port, (listenToken) => {
      if (listenToken) {
        console.log(`WebSocket server listening on port ${port}`);
        token = listenToken;
      } else {
        console.log("Failed to listen on port " + port);
      }
    });

  return {
    app,
    stop: () => {
      if (token) {
        uWS.us_listen_socket_close(token);
      }
    },
  };
}

module.exports = { startServer };
