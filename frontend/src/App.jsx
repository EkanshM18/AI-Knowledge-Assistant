import { useEffect, useState } from 'react'

import { fetchHealth, fetchStats, sendMessage, uploadDocuments } from './api/client'
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

function getSessionId(botId) {
  const storageKey = `${botId}-session-id`
  const existing = window.localStorage.getItem(storageKey)
  if (existing) {
    return existing
  }
  const created = window.crypto?.randomUUID?.() ?? `${Date.now()}-session`
  window.localStorage.setItem(storageKey, created)
  return created
}

export default function App() {
  const [activeBot, setActiveBot] = useState('enterprise')
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [conversationState, setConversationState] = useState(() =>
    Object.fromEntries(
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
  )
  const [uploading, setUploading] = useState(false)
  const [sending, setSending] = useState(false)
  const [status, setStatus] = useState('Loading local services...')
  const [sessionIds] = useState(() =>
    Object.fromEntries(bots.map((bot) => [bot.id, getSessionId(bot.id)]))
  )

  const currentConversation = conversationState[activeBot]

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
                Dual-Bot Local Assistant
              </div>
              <h1 className="mt-5 text-4xl font-extrabold leading-tight md:text-5xl">
                One workspace for grounded enterprise search and lightweight general tools.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-8 text-slate">
                FastAPI, Qdrant, Hugging Face models, and LangGraph orchestration with separate enterprise and
                general assistant flows.
              </p>
            </div>
            <div className="rounded-[1.8rem] bg-ink px-5 py-4 text-white">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-white/70">Runtime Status</div>
              <div className="mt-2 text-lg font-semibold">{status}</div>
            </div>
          </div>
        </section>

        <BotSelector bots={bots} activeBot={activeBot} onSelect={setActiveBot} />

        <HeaderStats health={health} stats={stats} />

        <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
          <div className="space-y-6">
            {activeBot === 'enterprise' && <UploadPanel onUpload={handleUpload} uploading={uploading} />}
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
      </div>
    </main>
  )
}
