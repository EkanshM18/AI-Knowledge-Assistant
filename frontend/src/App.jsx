import { useEffect, useState } from 'react'

import { fetchHealth, fetchStats, sendMessage, uploadDocuments } from './api/client'
import { ChatPanel } from './components/ChatPanel'
import { HeaderStats } from './components/HeaderStats'
import { SourcePanel } from './components/SourcePanel'
import { UploadPanel } from './components/UploadPanel'

const initialMessages = [
  {
    role: 'assistant',
    content:
      'Upload internal documents and I will answer using only the indexed enterprise knowledge with source grounding.'
  }
]

function getSessionId() {
  const existing = window.localStorage.getItem('enterprise-session-id')
  if (existing) {
    return existing
  }
  const created = window.crypto?.randomUUID?.() ?? `${Date.now()}-session`
  window.localStorage.setItem('enterprise-session-id', created)
  return created
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [messages, setMessages] = useState(initialMessages)
  const [sources, setSources] = useState([])
  const [grounded, setGrounded] = useState(false)
  const [validationNotes, setValidationNotes] = useState('')
  const [uploading, setUploading] = useState(false)
  const [sending, setSending] = useState(false)
  const [status, setStatus] = useState('Loading local services...')
  const [sessionId] = useState(getSessionId)

  async function refreshStats() {
    const [healthResponse, statsResponse] = await Promise.all([fetchHealth(), fetchStats()])
    setHealth(healthResponse)
    setStats(statsResponse)
  }

  useEffect(() => {
    refreshStats()
      .then(() => setStatus('Local stack ready'))
      .catch((error) => setStatus(error.message))
  }, [])

  async function handleUpload(files, tags) {
    try {
      setUploading(true)
      setStatus('Indexing uploaded documents into local Qdrant...')
      await uploadDocuments(files, tags)
      await refreshStats()
      setStatus('Documents indexed successfully')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleSend(message) {
    const userMessage = { role: 'user', content: message }
    setMessages((current) => [...current, userMessage])
    setSending(true)
    setStatus('Running retrieval and agent orchestration...')

    try {
      const response = await sendMessage({
        message,
        session_id: sessionId
      })
      setMessages((current) => [...current, { role: 'assistant', content: response.answer }])
      setSources(response.sources ?? [])
      setGrounded(response.grounded)
      setValidationNotes(response.validation_notes)
      setStatus(`Route: ${response.route}`)
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: `Request failed: ${error.message}`
        }
      ])
      setStatus(error.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <main className="min-h-screen bg-mesh px-4 py-8 text-ink md:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="overflow-hidden rounded-[2.4rem] border border-white/70 bg-white/70 px-6 py-8 shadow-panel backdrop-blur md:px-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="rounded-full bg-ink px-4 py-2 text-xs font-bold uppercase tracking-[0.26em] text-white w-fit">
                Enterprise RAG Platform
              </div>
              <h1 className="mt-5 text-4xl font-extrabold leading-tight md:text-5xl">
                Local multi-agent knowledge assistant for internal enterprise data.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-8 text-slate">
                FastAPI, LlamaIndex, Qdrant local mode, Hugging Face models, and LangGraph orchestration in a
                production-style portfolio build.
              </p>
            </div>
            <div className="rounded-[1.8rem] bg-ink px-5 py-4 text-white">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-white/70">Runtime Status</div>
              <div className="mt-2 text-lg font-semibold">{status}</div>
            </div>
          </div>
        </section>

        <HeaderStats health={health} stats={stats} />

        <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
          <div className="space-y-6">
            <UploadPanel onUpload={handleUpload} uploading={uploading} />
            <ChatPanel
              messages={messages}
              onSend={handleSend}
              sending={sending}
              grounded={grounded}
              validationNotes={validationNotes}
            />
          </div>
          <SourcePanel sources={sources} />
        </div>
      </div>
    </main>
  )
}
