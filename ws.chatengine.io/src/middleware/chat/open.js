export default function open(ws) {
  const channel = `chat:${ws.id}`;
  console.log(`Open channel: ${channel}`);
  ws.subscribe(channel); // Picks up app.publish(channel, message)
}