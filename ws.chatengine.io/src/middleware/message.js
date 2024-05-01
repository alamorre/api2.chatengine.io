export default function message(ws, message, isBinary) {
  ws.send(message, isBinary);
}
