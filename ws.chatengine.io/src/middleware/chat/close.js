export default function close() {
  const channel = `chat:${ws.chatID}`;
  console.log(`Close channel: ${channel}`);
}
