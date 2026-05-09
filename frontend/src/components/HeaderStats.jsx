export function HeaderStats({ health, stats }) {
  const cards = [
    {
      label: 'Vector Count',
      value: health?.vector_count ?? 0
    },
    {
      label: 'Indexed Files',
      value: health?.unique_files ?? 0
    },
    {
      label: 'Collection',
      value: stats?.collection_name ?? 'enterprise_knowledge'
    }
  ]

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-panel backdrop-blur"
        >
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate">
            {card.label}
          </div>
          <div className="mt-3 text-2xl font-extrabold text-ink">{card.value}</div>
        </div>
      ))}
    </div>
  )
}

