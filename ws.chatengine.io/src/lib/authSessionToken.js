import axios from "axios";

import { redisCache } from "./redis.js";

export default async function authSessionToken(sessionToken) {
  const cacheKey = `session-${sessionToken}`;

  // Try to get cached result from Redis
  const cachedResult = await redisCache.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cacheKey}=${cachedResult}`);
    return { success: cachedResult != "-1", id: cachedResult }; // Redis stores data as strings
  }

  try {
    const url = `${process.env.API_URL}/users/me/session/${sessionToken}/`;
    const response = await axios.get(url);
    const id = response.data.id.toString();
    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    await redisCache.set(cacheKey, id, "EX", 900);
    return { success: true, id };
  } catch (error) {
    console.log("Sessiont token auth failed", error);
    await redisCache.set(cacheKey, "-1", "EX", 900);
    return { success: false, error };
  }
}
