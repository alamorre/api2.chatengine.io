import { WebSocket } from "ws";
import uWS from "uWebSockets.js";

import { app } from "../src/server";

describe("WebSocket Server Tests", () => {
  let token;
  const port = 9001;

  beforeAll((done) => {
    app.listen(port, (listenToken) => {
      console.log(`Test server started on port ${port}`);
      token = listenToken;
      done();
    });
  });

  afterAll((done) => {
    uWS.us_listen_socket_close(token);
    console.log("Test server stopped");
    done();
  });

  test("Server should be online and echo messages", (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);

    client.on("open", () => {
      console.log("Connection established with test server.");
      client.send("Hello server");
    });

    client.on("message", (message) => {
      expect(message.toString()).toBe("Hello server");
      client.close();
    });

    client.on("close", () => {
      console.log("WebSocket closed");
      done();
    });

    client.on("error", (err) => {
      console.error("WebSocket encountered error:", err);
      done(err);
    });
  });
});
