import WebSocket from "ws";

const projectId = "c5394dc3-a877-4125-ace1-4baed7a98447";
const chatID = "1";
const accessKey = "ca-5573dea9-d7f1-4959-944e-267b8ce93935";

const ws = new WebSocket(
  `ws://localhost:9001/ws/chat/?project-id=${projectId}&chat-id=${chatID}&access-key=${accessKey}`
);

const username = "adam";
const secret = "pass1234";

const ws2 = new WebSocket(
  `ws://localhost:9001/ws/person/?project-id=${projectId}&user-name=${username}&user-secret=${secret}`
);
