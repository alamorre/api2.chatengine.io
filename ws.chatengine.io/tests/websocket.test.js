const WebSocket = require("ws");
const { startServer } = require("../src/server"); // Correct import of your server setup

describe("WebSocket Server Tests", () => {
  let server;
  let client;

  beforeAll((done) => {
    server = startServer();
    client = new WebSocket("ws://localhost:9001");
    client.on("open", done);
  });

  afterAll(() => {
    client.close();
    // server.us_listen_socket.close(); // uWebSocket auomatically closes the server when the process exits
  });

  test("Server echoes messages", (done) => {
    const message = "Hello WebSocket!";
    client.on("message", (data) => {
      // Ensure data is converted to a string if it's a Buffer
      const receivedMessage =
        data instanceof Buffer ? data.toString("utf8") : data;
      expect(receivedMessage).toBe(message);
      done();
    });
    client.send(message, done);
  });
});
