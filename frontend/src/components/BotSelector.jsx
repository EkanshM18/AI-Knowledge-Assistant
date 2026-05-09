export function BotSelector({ bots, activeBot, onSelect }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {bots.map((bot) => {
        const isActive = bot.id === activeBot
        return (
          <button
            key={bot.id}
            type="button"
            onClick={() => onSelect(bot.id)}
            className={[
              'rounded-[2rem] border p-5 text-left transition duration-200',
              isActive
                ? 'border-ink bg-ink text-white shadow-panel'
                : 'border-white/70 bg-white/75 text-ink hover:border-accent hover:bg-white'
            ].join(' ')}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-lg font-extrabold">{bot.name}</div>
                <p className={`mt-2 text-sm leading-7 ${isActive ? 'text-white/75' : 'text-slate'}`}>
                  {bot.description}
                </p>
              </div>
              <div
                className={[
                  'rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.22em]',
                  isActive ? 'bg-white/12 text-white' : 'bg-accent/10 text-accent'
                ].join(' ')}
              >
                {bot.badge}
              </div>
            </div>
          </button>
        )
      })}
    </div>
  )
}

