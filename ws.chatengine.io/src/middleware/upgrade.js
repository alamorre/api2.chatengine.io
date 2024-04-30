export default function upgrade(res, req, context) {
  const publicKey = req.getHeader("public-key");
  const username = req.getHeader("username");
  const secret = req.getHeader("secret");

  if (publicKey === "abc" && username === "adam" && secret === "pass1234") {
    res.upgrade(
      { publicKey, username, secret }, // Attach properties to ws object if needed
      req.getHeader("sec-websocket-key"), // Required headers
      req.getHeader("sec-websocket-protocol"), // Required headers
      req.getHeader("sec-websocket-extensions"), // Required headers
      context
    );
  } else {
    res.writeStatus("401 Unauthorized").end();
  }
}
