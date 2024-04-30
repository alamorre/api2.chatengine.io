import axios from "axios";

const url = "http://127.0.0.1:8000/health/";

export default function auth(publicKey, username, secret) {
  return axios
    .get(url, {
      headers: {
        "public-key": publicKey,
        username: username,
        secret: secret,
      },
    })
    .then((response) => {
      if (response.status === 200) {
        return true; // Authenticated
      } else {
        return false; // Not authenticated
      }
    })
    .catch((e) => {
      console.log("Upgraded failed", e);
      return false;
    });
}
