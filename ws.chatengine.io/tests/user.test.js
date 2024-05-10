import WebSocket from "ws";
import uWS from "uWebSockets.js";
import axios from "axios";

import app from "../src/app.js";
import { redisCache, redisSubscriber } from "../src/lib/redis.js";

describe("WebSocket Person Tests", () => {
  let token;
  let client;
  const wsUrl = "ws://localhost:9001/person/";
  const projectId = "c5394dc3-a877-4125-ace1-4baed7a98447";
  const privateKey = "6d3b85b2-000a-427f-86e0-76c41f6cd5ec";
  const username = "adam";
  const secret = "pass1234";

  beforeAll((done) => {
    redisCache.flushall();
    app.listen(9001, (listenToken) => {
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

  beforeEach(() => {
    axios.get.mockClear();
  });

  test("Authenticate person successfully without caching", (done) => {
    const expectedApiResponse = { status: 200, data: { id: 1 } };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const url = `${wsUrl}?projectID=${projectId}&username=${username}&secret=${secret}`;
    client = new WebSocket(url);

    const options = {
      headers: {
        "project-id": projectId,
        "user-name": username,
        "user-secret": secret,
      },
    };

    client.onopen = () => {
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/users/me/`,
        { ...options, headers: { ...options.headers, "private-key": false } }
      );

      client.send("Hello, world!");
    };

    client.onmessage = (event) => {
      expect(event.data).toBe("Hello, world!");
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).toBeTruthy();
      done();
    };
  });

  test("Authenticate person successfully with caching", (done) => {
    const cacheKey = `auth-${projectId}-${username}-${secret}-`;
    redisCache.set(cacheKey, 1, "EX", 900);

    const url = `${wsUrl}?projectID=${projectId}&username=${username}&secret=${secret}`;
    client = new WebSocket(url);

    client.onopen = () => {
      expect(axios.get).not.toHaveBeenCalled();
      client.send("Hello, world!");
    };

    client.onmessage = (event) => {
      expect(event.data).toBe("Hello, world!");
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).toBeTruthy();
      done();
    };
  });

  test("Authenticate person unsuccessfully without caching", (done) => {
    const expectedApiResponse = { status: 401, data: {} };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const badProjectId = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
    const url = `${wsUrl}?projectID=${badProjectId}&username=${username}&secret=${secret}`;
    client = new WebSocket(url);

    const options = {
      headers: {
        "project-id": badProjectId,
        "user-name": username,
        "user-secret": secret,
      },
    };

    client.onerror = (event) => {
      expect(event.message).toBe("Unexpected server response: 401");
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/users/me/`,
        { ...options, headers: { ...options.headers, "private-key": false } }
      );
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).not.toBeTruthy();
      done();
    };
  });

  test("Authenticate person unsuccessfully with caching", (done) => {
    const badProjectId = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
    const cacheKey = `auth-${badProjectId}-${username}-${secret}-`;
    redisCache.set(cacheKey, "-1", "EX", 900);

    const url = `${wsUrl}?projectID=${badProjectId}&username=${username}&secret=${secret}`;
    client = new WebSocket(url);

    client.onerror = (event) => {
      expect(axios.get).not.toHaveBeenCalled();
      expect(event.message).toBe("Unexpected server response: 401");
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).not.toBeTruthy();
      done();
    };
  });

  test("Authenticate person with private key", (done) => {
    const expectedApiResponse = { status: 200, data: { id: 1 } };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const url = `${wsUrl}?privateKey=${privateKey}&username=${username}&secret=${secret}`;
    client = new WebSocket(url);

    const options = {
      headers: {
        "private-key": privateKey,
        "user-name": username,
        "user-secret": secret,
      },
    };

    client.onopen = () => {
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/users/me/`,
        { ...options, headers: { ...options.headers, "project-id": false } }
      );

      client.send("Hello, world!");
    };

    client.onmessage = (event) => {
      expect(event.data).toBe("Hello, world!");
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).toBeTruthy();
      done();
    };
  });
});
