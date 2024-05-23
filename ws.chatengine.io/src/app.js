import uWS from "uWebSockets.js";
import { withErrorHandling } from "./lib/sentry.js";

import upgradePerson from "./middleware/person/upgrade.js";
import openPerson from "./middleware/person/open.js";
import messagePerson from "./middleware/person/message.js";
import closePerson from "./middleware/person/close.js";

import upgradeChat from "./middleware/chat/upgrade.js";
import openChat from "./middleware/chat/open.js";
import messageChat from "./middleware/chat/message.js";
import closeChat from "./middleware/chat/close.js";

import { redisSubscriber } from "./lib/redis.js";

import dotenv from "dotenv";

dotenv.config();

// Server
const app = uWS.App();

// Define WebSocket route for /person_v4/
app.ws("/person_v4/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade: withErrorHandling(upgradePerson, {
    route: "/person_v4/",
    stage: "upgrade",
  }),
  open: withErrorHandling(openPerson, { route: "/person_v4/", stage: "open" }),
  message: withErrorHandling(messagePerson, {
    route: "/person_v4/",
    stage: "message",
  }),
  close: withErrorHandling(closePerson, {
    route: "/person_v4/",
    stage: "close",
  }),
});

// Define WebSocket route for /chat/
app.ws("/chat/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade: withErrorHandling(upgradeChat, {
    route: "/chat/",
    stage: "upgrade",
  }),
  open: withErrorHandling(openChat, { route: "/chat/", stage: "open" }),
  message: withErrorHandling(messageChat, {
    route: "/chat/",
    stage: "message",
  }),
  close: withErrorHandling(closeChat, { route: "/chat/", stage: "close" }),
});

// HTTP route for health check
app.get("/health/", (res, req) => {
  res.writeStatus("200 OK").end("Healthy");
});

// Default handler for any other request
app.any("/*", (res) => {
  res.end("Nothing to see here!");
});

redisSubscriber.on("message", (channel, message) => {
  app.publish(channel, message);
  console.log(`Publishing message to ${channel}`);
});

export default app;
