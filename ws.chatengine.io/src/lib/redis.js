import { Redis } from "ioredis";

export const redisCache = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  db: 0, // 0 for caching
});

export const redisSubscriber = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  db: 1, // 1 for pub/sub
});
