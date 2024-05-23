import { redisSubscriber } from "../../lib/redis.js";

export default function openPerson(ws) {
  const channel = `person:${ws.id}`;
  ws.subscribe(channel); // Picks up app.publish(channel, message)
  redisSubscriber.subscribe(channel);
  console.log(`Open channel: ${channel}`);
}
