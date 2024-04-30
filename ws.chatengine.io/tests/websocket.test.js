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
    server.us_listen_socket.close(); // Close the uWebSocket server properly
  });

  test("Server echoes messages", (done) => {
    const message = "Hello WebSocket!";
    client.on("message", (data) => {
      expect(data).toBe(message);
      done();
    });
    client.send(message);
  });
});
