import auth from "../../lib/auth.js";

export default function upgrade(res, req, context) {
  // Extract headers synchronously
  const project = req.getHeader("project-id");
  const username = req.getHeader("user-name");
  const secret = req.getHeader("user-secret");
  const secWebSocketKey = req.getHeader("sec-websocket-key");
  const secWebSocketProtocol = req.getHeader("sec-websocket-protocol");
  const secWebSocketExtensions = req.getHeader("sec-websocket-extensions");

  // Attach an abort handler to handle the case where the request is aborted mid-operation
  res.onAborted(() => {
    console.error("Request was aborted by the client");
    res.aborted = true; // You can use a flag to check if the response was aborted
  });

  auth(project, username, secret)
    .then((authenticated) => {
      if (res.aborted) return; // Do not use res if it has been marked as aborted

      // Use cork to buffer writes
      res.cork(() => {
        if (authenticated) {
          res.upgrade(
            { project, username, secret }, // Attach properties to ws object if needed
            secWebSocketKey, // Use pre-extracted header
            secWebSocketProtocol, // Use pre-extracted header
            secWebSocketExtensions, // Use pre-extracted header
            context
          );
        } else {
          res.writeStatus("401 Unauthorized").end();
        }
      });
    })
    .catch((e) => {
      if (res.aborted) return; // Do not use res if it has been marked as aborted

      // Use cork to buffer writes
      res.cork(() => {
        console.error("Authentication failed with error:", e);
        res.writeStatus("500 Internal Server Error").end();
      });
    });
}
