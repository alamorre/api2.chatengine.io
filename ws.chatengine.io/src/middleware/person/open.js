import { redis } from "../../main.js";

export default function openPerson(ws) {
  const channel = `person:${ws.id}`;
  console.log(`Open channel: ${channel}`);
  redis.subscribe(channel);
}
