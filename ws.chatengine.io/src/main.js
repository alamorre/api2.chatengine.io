import dotenv from "dotenv";
import app from "./app.js";

dotenv.config();

const port = 9001;

app.listen(port, (listenToken) => {
  if (listenToken) {
    console.log(`WebSocket listening on port ${port}`);
  } else {
    console.log(`Failed to listen on port ${port}`);
  }
});
