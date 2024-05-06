import { redis } from "../../lib/redis.js";

export default function closePerson(ws) {
  const channel = `person:${ws.id}`;
  console.log(`Close channel: ${channel}`);
  redis.unsubscribe(channel);
  ws.unsubscribe(channel);
}
