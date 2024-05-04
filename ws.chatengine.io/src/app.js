import uWS from "uWebSockets.js";
import upgrade from "./middleware/person/upgrade.js";
import open from "./middleware/person/open.js";
import message from "./middleware/person/message.js";
import close from "./middleware/person/close.js";

// Server
const app = uWS.App();

// Define WebSocket route for /ws/person/
app.ws("/ws/person/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade,
  open,
  message,
  close,
});

// Define WebSocket route for /ws/chat/
app.ws("/ws/chat/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade,
  open,
  message,
  close,
});

// HTTP route for health check
app.get("/ws/health/", (res, req) => {
  res.writeStatus("200 OK").end("Healthy");
});

// Default handler for any other request
app.any("/*", (res) => {
  res.end("Nothing to see here!");
});

export default app;
