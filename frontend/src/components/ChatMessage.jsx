export function ChatMessage({ message }) {
  const isAssistant = message.role === 'assistant'

  return (
    <div className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      <div
        className={[
          'max-w-[85%] rounded-[1.6rem] px-5 py-4 shadow-sm',
          isAssistant ? 'bg-white text-ink' : 'bg-ink text-white'
        ].join(' ')}
      >
        <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.22em] opacity-70">
          {isAssistant ? 'Assistant' : 'You'}
        </div>
        <div className="whitespace-pre-wrap text-sm leading-7">{message.content}</div>
      </div>
    </div>
  )
}

