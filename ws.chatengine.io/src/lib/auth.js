import axios from "axios";

import { redisCache } from "./redis.js";

export default async function auth(project, username, secret, privateKey) {
  const cacheKey = `auth-${project}-${username}-${secret}-${privateKey}`;

  // Try to get cached result from Redis
  const cachedResult = await redisCache.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cacheKey}=${cachedResult}`);
    return { success: cachedResult != "-1", id: cachedResult }; // Redis stores data as strings
  }

  try {
    const url = `${process.env.API_URL}/users/me/`;
    const response = await axios.get(url, {
      headers: {
        "project-id": project !== "" && project,
        "user-name": username !== "" && username,
        "user-secret": secret !== "" && secret,
        "private-key": privateKey !== "" && privateKey,
      },
    });

    if (response.status !== 200) {
      throw new Error("Invalid project, username, or secret");
    }

    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    const id = response.data.id.toString();
    await redisCache.set(cacheKey, id, "EX", 300);
    return { success: true, id };
  } catch (error) {
    console.log("Auth failed", error);
    await redisCache.set(cacheKey, "-1", "EX", 300);
    return { success: false, error };
  }
}
