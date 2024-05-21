import uWS from "uWebSockets.js";

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

// Define WebSocket route for /person/
app.ws("/person_v4/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade: upgradePerson,
  open: openPerson,
  message: messagePerson,
  close: closePerson,
});

// Define WebSocket route for /chat/
app.ws("/chat/", {
  compression: uWS.SHARED_COMPRESSOR,
  maxPayloadLength: 16 * 1024 * 1024,
  idleTimeout: 300,
  upgrade: upgradeChat,
  open: openChat,
  message: messageChat,
  close: closeChat,
});

// HTTP route for health check
app.get("/health/", (res, req) => {
  res.writeStatus("200 OK").end("Healthy");
});

// Default handler for any other request
app.any("/*", (res) => {
  res.end("Nothing to see here!");
});

redisSubscriber.psubscribe("person:*", "chat:*");

redisSubscriber.on("pmessage", (_, channel, message) => {
  console.log(`Publishing message to ${channel}`);
  app.publish(channel, message);
});

export default app;
