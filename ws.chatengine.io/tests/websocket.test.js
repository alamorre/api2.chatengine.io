const WebSocket = require("ws");
const { startServer } = require("../src/server");

describe("WebSocket Server Tests", () => {
  let server;
  let client;

  beforeAll((done) => {
    server = startServer();
    client = new WebSocket("ws://localhost:9001");
    client.on("open", done);
  });

  afterAll((done) => {
    // Close the client and ensure it closes before stopping the server
    client.on("close", () => {
      server.stop(); // Stop the server after client disconnects
      done(); // Finish the cleanup process
    });

    client.close(); // Initiates the closing of the WebSocket client
  });

  test("Server echoes messages", (done) => {
    const message = "Hello WebSocket!";
    client.on("message", (data) => {
      const receivedMessage =
        data instanceof Buffer ? data.toString("utf8") : data;
      expect(receivedMessage).toBe(message);
      done();
    });
    client.send(message, done);
  });
});
