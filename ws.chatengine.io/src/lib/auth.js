import axios from "axios";

const url = "http://127.0.0.1:8000/health/";

export default async function auth(publicKey, username, secret) {
  try {
    const response = await axios.get(url, {
      headers: {
        "public-key": publicKey,
        username: username,
        secret: secret,
      },
    });
    return response.status === 200;
  } catch (e) {
    console.log("Upgraded failed", e);
    return false;
  }
}
