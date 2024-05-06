// src/server.ts
import uWS from "uWebSockets.js";

const app = uWS.App();

app.ws("/*", {
  open: (ws) => {
    console.log("A WebSocket connection has been opened.");
  },
  message: (ws, message, isBinary) => {
    ws.send(message, isBinary);
  },
  close: (ws, code, message) => {
    console.log("WebSocket closed");
  },
});

export { app };
