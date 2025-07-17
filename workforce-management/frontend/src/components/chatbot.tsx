import React, { useState, useRef, useEffect } from 'react';
import { fetchWorkers } from '../api';


export const Chatbot = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [open, setOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    let workerData = null;
    try {
      workerData = await fetchWorkers();
    } catch (err) {
      workerData = { error: 'Failed to fetch workers' };
    }
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    setInput('');
    const requestBody = {
      message: input,
      data: workerData
    };
    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      const result = await response.json();
      console.log('AI response:', result);
      setMessages(msgs => [
        ...msgs,
        { sender: 'bot', text: result?.analysis || 'No response from server.' }
      ]);
    } catch (error) {
      setMessages(msgs => [
        ...msgs,
        { sender: 'bot', text: 'Sorry, there was an error connecting to the AI service.' }
      ]);
    }
  };

  return (
    <>
      {!open && (
        <button
          style={styles.fab}
          aria-label="Open chat"
          onClick={() => setOpen(true)}
        >
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="16" fill="#4f8cff" />
            <path d="M10 13h12v6a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2v-6z" fill="#fff"/>
            <rect x="10" y="11" width="12" height="4" rx="2" fill="#fff"/>
          </svg>
        </button>
      )}

      {open && (
        <>
          <div style={styles.overlay} onClick={() => setOpen(false)} />
          <div style={styles.container}>
            <div style={styles.header}>
              WMS Chatbot
              <button
                style={styles.closeBtn}
                aria-label="Close chat"
                onClick={() => setOpen(false)}
              >
                ×
              </button>
            </div>
            <div style={styles.chatArea}>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    ...styles.message,
                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                    background: msg.sender === 'user' ? '#4f8cff' : '#e5e5ea',
                    color: msg.sender === 'user' ? '#fff' : '#222',
                  }}
                >
                  {msg.text}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <form style={styles.inputArea} onSubmit={handleSend}>
              <input
                style={styles.input}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Type your message..."
                autoFocus
              />
              <button style={styles.button} type="submit">Send</button>
            </form>
          </div>
        </>
      )}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  fab: {
    position: 'fixed',
    bottom: 32,
    right: 32,
    width: 64,
    height: 64,
    borderRadius: '50%',
    background: 'none',
    border: 'none',
    boxShadow: '0 4px 16px rgba(79,140,255,0.18)',
    cursor: 'pointer',
    zIndex: 1002,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 0,
    transition: 'box-shadow 0.2s',
  },
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    background: 'rgba(0,0,0,0.18)',
    zIndex: 1000,
    transition: 'background 0.2s',
  },
  container: {
    position: 'fixed',
    bottom: 110,
    right: 40,
    width: 350,
    height: 500,
    display: 'flex',
    flexDirection: 'column',
    borderRadius: 16,
    boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
    background: '#fff',
    overflow: 'hidden',
    fontFamily: 'Inter, Arial, sans-serif',
    zIndex: 1003,
    animation: 'chatbox-fade-in 0.2s',
  },
  header: {
    background: 'linear-gradient(90deg, #4f8cff 0%, #3358ff 100%)',
    color: '#fff',
    padding: '18px 20px',
    fontSize: 20,
    fontWeight: 600,
    letterSpacing: 1,
    textAlign: 'center',
    position: 'relative',
  },
  closeBtn: {
    position: 'absolute',
    right: 16,
    top: 12,
    background: 'none',
    border: 'none',
    color: '#fff',
    fontSize: 28,
    fontWeight: 400,
    cursor: 'pointer',
    lineHeight: 1,
    zIndex: 1,
  },
  chatArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    padding: '18px 12px',
    gap: 10,
    overflowY: 'auto',
    background: '#f7f8fa',
  },
  message: {
    maxWidth: '75%',
    padding: '10px 16px',
    borderRadius: 18,
    marginBottom: 2,
    fontSize: 15,
    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
    wordBreak: 'break-word',
  },
  inputArea: {
    display: 'flex',
    padding: '14px 12px',
    borderTop: '1px solid #e5e5ea',
    background: '#fff',
    gap: 8,
  },
  input: {
    flex: 1,
    padding: '10px 14px',
    borderRadius: 20,
    border: '1px solid #d1d5db',
    fontSize: 15,
    outline: 'none',
    background: '#f7f8fa',
    marginRight: 4,
  },
  button: {
    background: 'linear-gradient(90deg, #4f8cff 0%, #3358ff 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: 20,
    padding: '10px 20px',
    fontWeight: 600,
    fontSize: 15,
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
};
