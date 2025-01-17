import auth from "../../lib/auth.js";
import authSessionToken from "../../lib/authSessionToken.js";

function getQueryParam(queryParameters, param) {
  const value = queryParameters.get(param);
  return value === null ? false : value;
}

export default function upgradePerson(res, req, context) {
  // Extract query parameters synchronously
  const query = req.getQuery();
  const queryParameters = new URLSearchParams(query);

  const sessionToken = getQueryParam(queryParameters, "session_token"); // For old authentication
  const project = getQueryParam(queryParameters, "projectID"); // For new authentication
  const username = getQueryParam(queryParameters, "username"); // For new authentication
  const secret = getQueryParam(queryParameters, "secret"); // For new authentication
  const privateKey = getQueryParam(queryParameters, "privateKey"); // For new authentication

  const secWebSocketKey = req.getHeader("sec-websocket-key");
  const secWebSocketProtocol = req.getHeader("sec-websocket-protocol");
  const secWebSocketExtensions = req.getHeader("sec-websocket-extensions");

  // Attach an abort handler to handle the case where the request is aborted mid-operation
  res.onAborted(() => {
    console.error("Request was aborted by the client");
    res.aborted = true; // You can use a flag to check if the response was aborted
  });

  if (sessionToken) {
    // Authenticate with session token
    authSessionToken(sessionToken)
      .then((response) => {
        if (res.aborted) return; // Do not use res if it has been marked as aborted
        // Use cork to buffer writes
        res.cork(() => {
          if (response.success) {
            res.upgrade(
              { sessionToken, id: response.id },
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
          console.error("Session token authentication failed with error:", e);
          res.writeStatus("500 Internal Server Error").end();
        });
      });
  } else {
    // Authenticate with project, username, secret, and private key
    auth(project, username, secret, privateKey)
      .then((response) => {
        if (res.aborted) return; // Do not use res if it has been marked as aborted
        // Use cork to buffer writes
        res.cork(() => {
          if (response.success) {
            res.upgrade(
              { project, username, secret, privateKey, id: response.id },
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
}
