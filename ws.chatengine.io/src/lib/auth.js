import axios from "axios";

import { redis } from "./redis.js";

export default async function auth(project, username, secret, pirvateKey) {
  const cacheKey = `auth-${project}-${username}-${secret}-${pirvateKey}`;

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
        "project-id": project !== "" && project,
        "user-name": username !== "" && username,
        "user-secret": secret !== "" && secret,
        "private-key": pirvateKey !== "" && pirvateKey,
      },
    });

    const isSuccess = response.status === 200;
    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    await redis.set(cacheKey, isSuccess.toString(), "EX", 900);
    return response;
  } catch (e) {
    console.log("Auth failed", e);
    await redis.set(cacheKey, "false", "EX", 900);
    return false;
  }
}
