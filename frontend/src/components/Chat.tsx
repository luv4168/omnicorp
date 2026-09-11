import { useState, useRef, useEffect, FormEvent } from 'react'
import './Chat.css'

interface Citation {
  document_id?: string
  title?: string
  source?: string
  chunk_id?: string
  relevance_score?: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  error?: string | null
  retrieved_chunks?: number
}

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I can answer questions about the OmniCorp Configuration Platform using the internal knowledge base.\n\nTry asking about configuration packages, the policy engine, deployment strategies, or common troubleshooting steps.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        error: data.error,
        retrieved_chunks: data.retrieved_chunks,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Sorry, something went wrong: ${err.message || 'Unknown error'}`,
          error: 'request_failed',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <div className="bubble">
              <div className="content">{m.content}</div>

              {m.citations && m.citations.length > 0 && (
                <div className="citations">
                  <div className="citations-label">Sources used</div>
                  <ul>
                    {m.citations.map((c, i) => (
                      <li key={i}>
                        <span className="doc-id">{c.document_id || '—'}</span>
                        <span className="doc-title">{c.title || c.source}</span>
                        {c.relevance_score != null && (
                          <span className="score">{(c.relevance_score * 100).toFixed(0)}%</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {m.error && m.error !== 'llm_not_configured' && (
                <div className="error-badge">Error: {m.error}</div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble loading">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about OmniCorp configuration…"
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}
