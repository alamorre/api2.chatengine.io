import { redisSubscriber } from "../../lib/redis.js";

export default function close(ws) {
  const channel = `chat:${ws.id}`;
  redisSubscriber.unsubscribe(channel);
  console.log(`Close channel: ${channel}`);
}
