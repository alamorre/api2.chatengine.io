const uWS = require("uWebSockets.js");

const port = 9001;

function startServer() {
  let token; // This will hold the listen token

  const app = uWS
    .App()
    .ws("/person", {
      compression: uWS.SHARED_COMPRESSOR,
      maxPayloadLength: 16 * 1024 * 1024,
      idleTimeout: 300,
      upgrade: (res, req, context) => {
        // Example of checking headers
        const publicKey = req.getHeader("public-key");
        const username = req.getHeader("username");
        const secret = req.getHeader("secret");
        if (
          publicKey === "abc" &&
          username === "adam" &&
          secret === "pass1234"
        ) {
          res.upgrade(
            { publicKey, username, secret }, // Attach properties to ws object if needed
            req.getHeader("sec-websocket-key"), // Required headers
            req.getHeader("sec-websocket-protocol"), // Required headers
            req.getHeader("sec-websocket-extensions"), // Required headers
            context
          );
        } else {
          res.writeStatus("401 Unauthorized").end();
        }
      },
      open: (ws) => {
        console.log("Custom Header in open:", ws.publicKey);
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
