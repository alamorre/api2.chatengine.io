export default function messagePerson(ws, message, isBinary) {
  ws.send(message, isBinary);
}
