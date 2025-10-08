import React, { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function App() {
  const [health, setHealth] = useState<string>('unknown')
  const [hardware, setHardware] = useState<any>(null)
  const [msg, setMsg] = useState('Hello')
  const [reply, setReply] = useState('')
  const [loading, setLoading] = useState(false)
  
  const checkHealth = async () => {
    const { data } = await axios.get(`${API}/health`)
    setHealth(data.status || 'ok')
  }

  const detectHardware = async () => {
    const { data } = await axios.get(`${API}/api/v1/hardware/detect`)
    setHardware(data)
  }

  const sendChat = async () => {
    setLoading(true)
    setReply('')
    try {
      const { data } = await axios.post(`${API}/api/v1/chat/send`, { message: msg, mode: 'chat', stream: false })
      const response = (data || []).find((x: any) => x.type === 'response')
      setReply(response ? response.content : JSON.stringify(data))
    } catch (e: any) {
      setReply(e.response?.data?.detail?.error || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', margin: 20 }}>
      <h1>Local AI Assistant</h1>
      <section style={{ marginBottom: 16 }}>
        <button onClick={checkHealth}>Check Backend Health</button>
        <span style={{ marginLeft: 8 }}>Status: {health}</span>
      </section>

      <section style={{ marginBottom: 16 }}>
        <button onClick={detectHardware}>Detect Hardware</button>
        {hardware && (
          <pre style={{ background: '#f5f5f5', padding: 12, overflow: 'auto' }}>{JSON.stringify(hardware, null, 2)}</pre>
        )}
      </section>

      <section>
        <h2>Chat</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <input value={msg} onChange={(e) => setMsg(e.target.value)} style={{ flex: 1 }} />
          <button onClick={sendChat} disabled={loading}>{loading ? 'Sending...' : 'Send'}</button>
        </div>
        {reply && (
          <pre style={{ background: '#f5f5f5', padding: 12, marginTop: 12, whiteSpace: 'pre-wrap' }}>{reply}</pre>
        )}
      </section>
    </div>
  )
}

import React from 'react';
import ChatInterface from './components/ChatInterface';

const App: React.FC = () => {
  return (
    <div className="h-screen flex flex-col">
      <ChatInterface />
    </div>
  );
};

export default App;