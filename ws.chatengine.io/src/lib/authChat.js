import axios from "axios";

import { redis } from "../lib/redis.js";

export default async function authChat(project, chatID, accessKey, pirvateKey) {
  const cacheKey = `chat-auth-${project}-${chatID}-${accessKey}-${pirvateKey}`;

  // Try to get cached result from Redis
  const cachedResult = await redis.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cachedResult}`);
    return cachedResult === "true"; // Redis stores data as strings
  }

  try {
    const url = `${process.env.API_URL}/chats/${chatID}/`;
    const response = await axios.get(url, {
      headers: {
        "project-id": project !== "" && project,
        "access-key": accessKey !== "" && accessKey,
        "private-key": pirvateKey !== "" && pirvateKey,
      },
    });

    const isSuccess = response.status === 200;
    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    await redis.set(cacheKey, isSuccess.toString(), "EX", 900);
    return isSuccess;
  } catch (e) {
    console.log("Auth chat failed", e.response && e.response.status);
    await redis.set(cacheKey, "false", "EX", 900);
    return false;
  }
}
