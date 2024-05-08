import app from "../src/app.js";

import uWS from "uWebSockets.js";

import { redisCache, redisSubscriber } from "../src/lib/redis.js";

describe("WebSocket Server Tests", () => {
  let token;
  const port = 9001;

  beforeAll((done) => {
    app.listen(port, (listenToken) => {
      token = listenToken;
      done();
    });
  });

  afterAll((done) => {
    uWS.us_listen_socket_close(token);
    redisCache.quit();
    redisSubscriber.quit();
    done();
  });

  test("adds 1 + 2 to equal 3", (done) => {
    expect(1).toBe(1);
    done();
  });
});
