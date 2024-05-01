import axios from "axios";

export default async function auth(project, username, secret) {
  try {
    const url = `${process.env.API_URL}/users/me/`;
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
