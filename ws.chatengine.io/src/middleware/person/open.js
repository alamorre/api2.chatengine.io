import { redis } from "../../lib/redis.js";

export default function openPerson(ws) {
  const channel = `person:${ws.id}`;
  console.log(`Open channel: ${channel}`);
  redis.subscribe(channel); // For horizontal scaling, use
  ws.subscribe(channel); // Picks up app.publish(channel, message)
}
