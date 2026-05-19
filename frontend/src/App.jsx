import { useEffect, useMemo, useState } from 'react'

import { fetchDocuments, fetchHealth, fetchStats, sendMessage, uploadDocuments } from './api/client'
import { BotSelector } from './components/BotSelector'
import { ChatPanel } from './components/ChatPanel'
import { EvidencePanel } from './components/EvidencePanel'
import { HeaderStats } from './components/HeaderStats'
import { UploadPanel } from './components/UploadPanel'

const bots = [
  {
    id: 'enterprise',
    name: 'Enterprise Bot',
    badge: 'RAG',
    description: 'Uses uploaded internal knowledge and source grounding for enterprise answers.',
    welcome:
      'Upload internal documents and I will answer using only the indexed enterprise knowledge with source grounding.'
  },
  {
    id: 'general',
    name: 'General Bot',
    badge: 'Tools',
    description: 'Handles weather, time, news, jokes, and normal conversation without the document store.',
    welcome: 'Ask for weather, time, news, a joke, or just chat normally.'
  }
]

function generateSessionId() {
  return window.crypto?.randomUUID?.() ?? `${Date.now()}-session`
}

function getSessionId(botId) {
  const storageKey = `${botId}-session-id`
  const existing = window.localStorage.getItem(storageKey)
  if (existing) return existing
  const created = generateSessionId()
  window.localStorage.setItem(storageKey, created)
  return created
}

function resetSessionId(botId) {
  const storageKey = `${botId}-session-id`
  const created = generateSessionId()
  window.localStorage.setItem(storageKey, created)
  return created
}

function getInitialConversationState() {
  return Object.fromEntries(
    bots.map((bot) => [
      bot.id,
      {
        messages: [{ role: 'assistant', content: bot.welcome }],
        sources: [],
        toolCalls: [],
        grounded: false,
        validationNotes: '',
        route: ''
      }
    ])
  )
}

export default function App() {
  const [activeBot, setActiveBot] = useState('enterprise')
  const [mode, setMode] = useState('select')
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [documents, setDocuments] = useState([])
  const [conversationState, setConversationState] = useState(getInitialConversationState)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [sending, setSending] = useState(false)
  const [status, setStatus] = useState('Connecting to cloud services...')
  const [sessionIds, setSessionIds] = useState(() =>
    Object.fromEntries(bots.map((bot) => [bot.id, getSessionId(bot.id)]))
  )

  const currentConversation = conversationState[activeBot]

  const title = useMemo(() => 'Enterprise AI Knowledge Assistant', [])

  async function refreshStats() {
    const [healthResponse, statsResponse, documentsResponse] = await Promise.all([
      fetchHealth(),
      fetchStats(),
      fetchDocuments()
    ])
    setHealth(healthResponse)
    setStats(statsResponse)
    setDocuments(documentsResponse.items ?? [])
  }

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      try {
        await refreshStats()
        if (!cancelled) {
          setStatus('Cloud stack ready')
        }
      } catch {
        if (!cancelled) {
          setStatus('Cloud services not reachable. Start FastAPI on http://127.0.0.1:8000 and try again.')
        }
      }
    }

    loadDashboard()

    const intervalId = window.setInterval(() => {
      refreshStats().catch(() => undefined)
    }, 15000)

    return () => {
      cancelled = true
      window.clearInterval(intervalId)
    }
  }, [])

  function resetBot(botId) {
    setActiveBot(botId)
    setSessionIds((current) => ({ ...current, [botId]: resetSessionId(botId) }))
    setConversationState((current) => {
      const next = { ...current }
      const bot = bots.find((b) => b.id === botId)
      next[botId] = {
        messages: [{ role: 'assistant', content: bot?.welcome ?? 'Ready.' }],
        sources: [],
        toolCalls: [],
        grounded: false,
        validationNotes: '',
        route: ''
      }
      return next
    })
    setUploading(false)
    setUploadProgress(0)
    setSending(false)
    setStatus('Workspace initialized')
  }

  async function handleUpload(files, tags) {
    try {
      setUploading(true)
      setUploadProgress(1)
      setStatus('Streaming to enterprise-documents bucket...')
      await uploadDocuments(files, tags, setUploadProgress)
      setStatus('Cloud upload successful. Triggering RAG ingestion...')
      await refreshStats()
      setStatus('Documents uploaded and ingestion status refreshed')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  async function handleSend(message) {
    const userMessage = { role: 'user', content: message }
    setConversationState((current) => ({
      ...current,
      [activeBot]: {
        ...current[activeBot],
        messages: [...current[activeBot].messages, userMessage]
      }
    }))
    setSending(true)
    setStatus(activeBot === 'enterprise' ? 'Running retrieval and agent orchestration...' : 'Running general tools...')

    try {
      const response = await sendMessage({
        message,
        bot_type: activeBot,
        session_id: sessionIds[activeBot]
      })
      setConversationState((current) => ({
        ...current,
        [activeBot]: {
          messages: [...current[activeBot].messages, { role: 'assistant', content: response.answer }],
          sources: response.sources ?? [],
          toolCalls: response.tool_calls ?? [],
          grounded: response.grounded,
          validationNotes: response.validation_notes,
          route: response.route ?? ''
        }
      }))
      setStatus(`Route: ${response.route}`)
    } catch (error) {
      setConversationState((current) => ({
        ...current,
        [activeBot]: {
          ...current[activeBot],
          messages: [
            ...current[activeBot].messages,
            {
              role: 'assistant',
              content: `Request failed: ${error.message}`
            }
          ]
        }
      }))
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
                Supabase Cloud Architecture
              </div>
              <h1 className="mt-5 text-4xl font-extrabold leading-tight md:text-5xl">{title}</h1>
              <p className="mt-4 max-w-3xl text-base leading-8 text-slate">
                Enterprise document upload, cloud storage, PostgreSQL metadata, async ingestion, Qdrant vectors,
                and grounded chat in one workspace.
              </p>
            </div>
            {mode === 'workspace' && (
              <div className="rounded-[1.8rem] bg-ink px-5 py-4 text-white">
                <div className="text-xs font-bold uppercase tracking-[0.22em] text-white/70">Runtime Status</div>
                <div className="mt-2 text-lg font-semibold">{status}</div>
              </div>
            )}
          </div>
        </section>

        {mode === 'select' ? (
          <section className="space-y-5">
            <div className="text-center">
              <div className="mx-auto w-fit rounded-full border border-white/70 bg-white/70 px-5 py-2 text-xs font-bold uppercase tracking-[0.22em]">
                Pick a bot to start
              </div>
            </div>

            <BotSelector
              bots={bots}
              activeBot={activeBot}
              onSelect={(botId) => {
                resetBot(botId)
                setMode('workspace')
              }}
            />
          </section>
        ) : (
          <>
            <BotSelector bots={bots} activeBot={activeBot} onSelect={(botId) => resetBot(botId)} />
            {activeBot === 'enterprise' ? <HeaderStats health={health} stats={stats} /> : null}

            <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
              <div className="space-y-6">
                {activeBot === 'enterprise' && (
                  <UploadPanel
                    onUpload={handleUpload}
                    uploading={uploading}
                    uploadProgress={uploadProgress}
                    documents={documents}
                  />
                )}
                <ChatPanel
                  bot={activeBot}
                  messages={currentConversation.messages}
                  onSend={handleSend}
                  sending={sending}
                  grounded={currentConversation.grounded}
                  validationNotes={currentConversation.validationNotes}
                />
              </div>
              <EvidencePanel
                bot={activeBot}
                sources={currentConversation.sources}
                toolCalls={currentConversation.toolCalls}
                route={currentConversation.route}
              />
            </div>
          </>
        )}
      </div>
    </main>
  )
}
