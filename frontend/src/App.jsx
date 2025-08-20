import { useEffect, useMemo, useState } from 'react'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

function ChatBubble({ from, text }){
  const isUser = from === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div className={`max-w-[75%] rounded-lg px-3 py-2 text-sm shadow ${isUser ? 'bg-blue-600 text-white' : 'bg-white text-gray-900'}`}>
        {text}
      </div>
    </div>
  )
}

export default function App(){
  const [email, setEmail] = useState('')
  const [messages, setMessages] = useState([
    { from: 'assistant', text: 'Hi! Login with Google and ask me to create a calendar event.' }
  ])
  const [input, setInput] = useState('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const e = params.get('email')
    if(e) setEmail(e)
  }, [])

  const login = async () => {
    const res = await fetch(`${BACKEND}/auth/google/login`)
    const data = await res.json()
    window.location.href = data.auth_url
  }

  const send = async () => {
    if(!input.trim()) return
    const userMsg = { from: 'user', text: input }
    setMessages(m => [...m, userMsg])
    setInput('')
    try{
      const res = await fetch(`${BACKEND}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, message: userMsg.text })
      })
      const data = await res.json()
      setMessages(m => [...m, { from: 'assistant', text: data.reply }])
    }catch(err){
      setMessages(m => [...m, { from: 'assistant', text: 'Error contacting server.' }])
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="p-4 bg-white shadow flex items-center justify-between">
        <h1 className="font-semibold">Agent Assistant</h1>
        <div className="flex items-center gap-3">
          {email ? <span className="text-sm text-gray-600">{email}</span> : null}
          <button onClick={login} className="px-3 py-1 bg-black text-white rounded">Login with Google</button>
        </div>
      </header>

      <main className="flex-1 container mx-auto p-4 max-w-3xl">
        <div className="bg-gray-50 border rounded p-3 h-[70vh] overflow-y-auto">
          {messages.map((m, i) => <ChatBubble key={i} from={m.from} text={m.text} />)}
        </div>
        <div className="mt-3 flex gap-2">
          <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Type a message..." className="flex-1 border rounded px-3 py-2" />
          <button onClick={send} className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
        </div>
      </main>
    </div>
  )
}
