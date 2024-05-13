import axios from "axios";

import { redisCache } from "../lib/redis.js";

export default async function authChat(project, chatID, accessKey, privateKey) {
  const cacheKey = `chat-auth-${project}-${chatID}-${accessKey}-${privateKey}`;

  // Try to get cached result from Redis
  const cachedResult = await redisCache.get(cacheKey);
  if (cachedResult !== null) {
    console.log(`Returning cached result: ${cacheKey}=${cachedResult}`);
    return { success: cachedResult != "-1", id: cachedResult };
  }

  try {
    const url = `${process.env.API_URL}/chats/${chatID}/`;
    const response = await axios.get(url, {
      headers: {
        "project-id": project !== "" && project,
        "access-key": accessKey !== "" && accessKey,
        "private-key": privateKey !== "" && privateKey,
      },
    });

    if (response.status !== 200) {
      throw new Error("Invalid project, chat ID, access key, or private key");
    }

    // Store the result in Redis with a TTL of 15 minutes (900 seconds)
    const id = response.data.id.toString();
    await redisCache.set(cacheKey, id, "EX", 900);
    return { success: true, id };
  } catch (error) {
    console.log("Chat auth failed", error);
    await redisCache.set(cacheKey, "-1", "EX", 900);
    return { success: false, error };
  }
}
