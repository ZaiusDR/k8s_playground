import React, { useEffect, useState } from "react";
import "./App.css"

const Messages = () => {
  const [messages, setMessages] = useState([]);
  const WEBSOCKET_URL = import.meta.env.VITE_WS_URL + "/ws";

  useEffect(() => {
    const socket = new WebSocket(WEBSOCKET_URL);

    socket.onmessage = (event) => {
      const newMessage = event.data;
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected. Attempting to reconnect...");
      setTimeout(() => window.location.reload(), 3000); // Auto-reconnect
    };

    return () => socket.close();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h2>Real-Time Messages</h2>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
};

export default Messages;
