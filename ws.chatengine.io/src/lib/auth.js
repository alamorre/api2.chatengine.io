import axios from "axios";

import { redisCache } from "./redis.js";

export default async function auth(project, username, secret, pirvateKey) {
  const cacheKey = `auth-${project}-${username}-${secret}-${pirvateKey}`;

  // Try to get cached result from Redis
  const cachedResult = await redisCache.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cachedResult}`);
    return { success: cachedResult != "-1", id: cachedResult }; // Redis stores data as strings
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
    const id = response.data.id.toString();
    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    await redisCache.set(cacheKey, id, "EX", 900);
    return { success: true, id };
  } catch (error) {
    console.log("Auth failed", error);
    await redisCache.set(cacheKey, "-1", "EX", 900);
    return { success: false, error };
  }
}
