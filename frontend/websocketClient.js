const token = process.argv[2];
if (!token) {
  console.error("Usage: node websocketClient.js <jwt_token>");
  process.exit(1);
}
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/notifications?token=${token}`);
ws.onmessage = (evt) => console.log("event:", evt.data);
ws.onopen = () => console.log("connected");
ws.onclose = () => console.log("closed");
