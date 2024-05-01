import dotenv from "dotenv";
import app from "./app.js";

import { Redis } from "ioredis";

dotenv.config();

export const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
});

const port = process.env.PORT || 9001;

app.listen(port, (listenToken) => {
  if (listenToken) {
    console.log(`WebSocket listening on port ${port}`);
  } else {
    console.log(`Failed to listen on port ${port}`);
  }
});
