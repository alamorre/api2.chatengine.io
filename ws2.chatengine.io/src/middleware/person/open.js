export default function openPerson(ws) {
  const channel = `person:${ws.id}`;
  console.log(`Open channel: ${channel}`);
  ws.subscribe(channel); // Picks up app.publish(channel, message)
}
