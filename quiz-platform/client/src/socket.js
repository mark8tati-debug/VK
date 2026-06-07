import { io } from "socket.io-client";

const URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:3001";

let socket;

export function getSocket() {
  if (!socket) socket = io(URL, { autoConnect: true });
  return socket;
}
