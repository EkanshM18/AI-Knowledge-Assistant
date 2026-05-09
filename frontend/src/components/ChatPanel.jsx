import { useState } from 'react'

import { ChatMessage } from './ChatMessage'

export function ChatPanel({ messages, onSend, sending, grounded, validationNotes }) {
  const [draft, setDraft] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (!draft.trim() || sending) {
      return
    }
    const message = draft
    setDraft('')
    await onSend(message)
  }

  return (
    <div className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-panel backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-ink">Knowledge Chat</h2>
          <p className="mt-2 text-sm text-slate">
            Ask grounded questions across the uploaded enterprise knowledge base.
          </p>
        </div>
        <div
          className={[
            'rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.2em]',
            grounded ? 'bg-accent/10 text-accent' : 'bg-coral/10 text-coral'
          ].join(' ')}
        >
          {grounded ? 'Grounded' : 'Awaiting evidence'}
        </div>
      </div>

      <div className="mt-6 h-[28rem] space-y-4 overflow-y-auto rounded-[1.7rem] bg-shell p-4">
        {messages.map((message, index) => (
          <ChatMessage key={`${message.role}-${index}`} message={message} />
        ))}
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-slate">
            Start by uploading documents, then ask a question.
          </div>
        )}
      </div>

      <div className="mt-4 rounded-3xl bg-shell px-4 py-3 text-sm text-slate">
        {validationNotes || 'Validation feedback will appear here after each answer.'}
      </div>

      <form onSubmit={handleSubmit} className="mt-5 flex gap-3">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          rows={3}
          placeholder="Ask about policies, reports, contracts, onboarding docs..."
          className="flex-1 resize-none rounded-[1.6rem] border border-mist bg-white px-4 py-3 outline-none transition focus:border-accent"
        />
        <button
          type="submit"
          disabled={sending}
          className="rounded-[1.6rem] bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          {sending ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

