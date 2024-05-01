import axios from "axios";

import { redis } from "../main.js";

export default async function auth(project, username, secret) {
  const cacheKey = `auth-${project}-${username}-${secret}`;

  // Try to get cached result from Redis
  const cachedResult = await redis.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cachedResult}`);
    return cachedResult === "true"; // Redis stores data as strings
  }

  try {
    const url = `${process.env.API_URL}/users/me/`;
    const response = await axios.get(url, {
      headers: {
        "project-id": project,
        "user-name": username,
        "user-secret": secret,
      },
    });

    const isSuccess = response.status === 200;
    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    await redis.set(cacheKey, isSuccess.toString(), "EX", 900);
    return isSuccess;
  } catch (e) {
    console.log("Auth failed", e.response && e.response.status);
    await redis.set(cacheKey, "false", "EX", 900);
    return false;
  }
}
