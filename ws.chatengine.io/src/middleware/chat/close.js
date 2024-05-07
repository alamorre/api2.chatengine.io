export default function close(ws) {
  const channel = `chat:${ws.id}`;
  console.log(`Close channel: ${channel}`);
}
