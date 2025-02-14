import { useState } from "react";
import './App.css'

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL;

  const sendMessage = async () => {
    if (!message) return alert("Message cannot be empty!");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      if (res.ok) {
        setResponse(`Message sent! ID: ${data.message_id}`);
      } else {
        setResponse(`Error: ${data.detail}`);
      }
    } catch (error) {
      setResponse("Failed to connect to server.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Send Message to SQS</h1>
      <textarea
        className="w-full max-w-md p-2 border border-gray-300 rounded-md"
        rows="4"
        placeholder="Type your message here..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button
        onClick={sendMessage}
        className="mt-3 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
      >
        Send Message
      </button>
      {response && <p className="mt-3 text-gray-700">{response}</p>}
    </div>
  );
}

export default App
