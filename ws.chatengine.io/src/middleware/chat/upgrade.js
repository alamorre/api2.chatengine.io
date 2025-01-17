import authChat from "../../lib/authChat.js";

function getQueryParam(queryParameters, param) {
  const value = queryParameters.get(param);
  return value === null ? false : value;
}

export default function upgradeChat(res, req, context) {
  // Extract query parameters synchronously
  const query = req.getQuery();
  const queryParameters = new URLSearchParams(query);
  const project = getQueryParam(queryParameters, "projectID");
  const chatID = getQueryParam(queryParameters, "chatID");
  const accessKey = getQueryParam(queryParameters, "accessKey");
  const privateKey = getQueryParam(queryParameters, "privateKey");

  // Extract headers synchronously
  const secWebSocketKey = req.getHeader("sec-websocket-key");
  const secWebSocketProtocol = req.getHeader("sec-websocket-protocol");
  const secWebSocketExtensions = req.getHeader("sec-websocket-extensions");

  // Attach an abort handler to handle the case where the request is aborted mid-operation
  res.onAborted(() => {
    console.error("Request was aborted by the client");
    res.aborted = true; // You can use a flag to check if the response was aborted
  });

  authChat(project, chatID, accessKey, privateKey)
    .then((response) => {
      if (res.aborted) return; // Do not use res if it has been marked as aborted

      // Use cork to buffer writes
      res.cork(() => {
        if (response.success) {
          res.upgrade(
            { project, chatID, accessKey, privateKey, id: response.id }, // Attach properties to ws object if needed
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
        console.log("Authentication chat failed with error:", e);
        res.writeStatus("500 Internal Server Error").end();
      });
    });
}
