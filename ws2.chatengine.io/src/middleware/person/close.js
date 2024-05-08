export default function closePerson(ws) {
  const channel = `person:${ws.id}`;
  console.log(`Close channel: ${channel}`);
}
