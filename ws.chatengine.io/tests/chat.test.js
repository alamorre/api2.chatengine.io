import WebSocket from "ws";
import uWS from "uWebSockets.js";
import axios from "axios";

import app from "../src/app.js";
import { redisCache, redisSubscriber } from "../src/lib/redis.js";

describe("WebSocket Chat Tests", () => {
  let token;
  let client;
  const wsUrl = "ws://localhost:9001/chat/";
  const projectId = "c5394dc3-a877-4125-ace1-4baed7a98447";
  const privateKey = "6d3b85b2-000a-427f-86e0-76c41f6cd5ec";
  const chatID = "1";
  const accessKey = "ca-5573dea9-d7f1-4959-944e-267b8ce93935";

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

  test("Authenticate chat without caching", (done) => {
    const expectedApiResponse = { status: 200, data: { id: 1 } };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const url = `${wsUrl}?projectID=${projectId}&chatID=${chatID}&accessKey=${accessKey}`;
    client = new WebSocket(url);

    client.onopen = () => {
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/chats/${chatID}/`,
        {
          headers: {
            "project-id": projectId,
            "access-key": accessKey,
            "private-key": false,
          },
        }
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

  test("Authenticate chat with caching", (done) => {
    const cacheKey = `chat-auth-${projectId}-${chatID}-${accessKey}-`;
    redisCache.set(cacheKey, 1, "EX", 900);

    const url = `${wsUrl}?projectID=${projectId}&chatID=${chatID}&accessKey=${accessKey}`;
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

  test("Reject chat without caching", (done) => {
    const expectedApiResponse = { status: 401, data: {} };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const badProjectId = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
    const url = `${wsUrl}?projectID=${badProjectId}&chatID=${chatID}&accessKey=${accessKey}`;
    client = new WebSocket(url);

    client.onerror = (event) => {
      expect(event.message).toBe("Unexpected server response: 401");
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/chats/${chatID}/`,
        {
          headers: {
            "project-id": badProjectId,
            "access-key": accessKey,
            "private-key": false,
          },
        }
      );
      client.close();
    };

    client.onclose = (event) => {
      expect(event.wasClean).not.toBeTruthy();
      done();
    };
  });

  test("Reject chat with caching", (done) => {
    const badProjectId = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
    const cacheKey = `chat-auth-${badProjectId}-${chatID}-${accessKey}-`;
    redisCache.set(cacheKey, "-1", "EX", 300);

    const url = `${wsUrl}?projectID=${badProjectId}&chatID=${chatID}&accessKey=${accessKey}`;
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

  test("Authenticate chat with private key", (done) => {
    const expectedApiResponse = { status: 200, data: { id: 1 } };
    axios.get.mockResolvedValueOnce(expectedApiResponse);

    const url = `${wsUrl}?privateKey=${privateKey}&chatID=${chatID}`;
    client = new WebSocket(url);

    client.onopen = () => {
      expect(axios.get).toHaveBeenCalledWith(
        `${process.env.API_URL}/chats/${chatID}/`,
        {
          headers: {
            "access-key": false,
            "private-key": privateKey,
            "project-id": false,
          },
        }
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
