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
    const url = `${process.env.API_URL}/users/session_auth/${sessionToken}/`;
    const response = await axios.get(url);

    if (response.status !== 200) {
      throw new Error("Invalid session token");
    }

    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    const id = response.data.user.id.toString();
    await redisCache.set(cacheKey, id, "EX", 300);
    return { success: true, id };
  } catch (error) {
    console.log("Sessiont token auth failed", error);
    await redisCache.set(cacheKey, "-1", "EX", 300);
    return { success: false, error };
  }
}
