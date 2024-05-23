import { redisSubscriber } from "../../lib/redis.js";

export default function open(ws) {
  const channel = `chat:${ws.id}`;
  ws.subscribe(channel); // Picks up app.publish(channel, message)
  redisSubscriber.subscribe(channel);
  console.log(`Open channel: ${channel}`);
}
