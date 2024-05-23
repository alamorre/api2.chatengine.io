import { redisSubscriber } from "../../lib/redis.js";

export default function closePerson(ws) {
  const channel = `person:${ws.id}`;
  redisSubscriber.unsubscribe(channel);
  console.log(`Close channel: ${channel}`);
}
