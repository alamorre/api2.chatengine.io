import axios from "axios";

const url = "http://127.0.0.1:8000/users/me/";

export default async function auth(project, username, secret) {
  try {
    const response = await axios.get(url, {
      headers: {
        "project-id": project,
        "user-name": username,
        "user-secret": secret,
      },
    });
    return response.status === 200;
  } catch (e) {
    console.log("Upgraded failed", e.response.status, e.response.statusText);
    return false;
  }
}
