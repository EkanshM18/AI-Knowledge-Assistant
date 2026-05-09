export function SourcePanel({ sources }) {
  return (
    <div className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-panel backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-extrabold text-ink">Grounding Sources</h2>
          <p className="mt-2 text-sm text-slate">
            Retrieved evidence used to generate the latest answer.
          </p>
        </div>
        <div className="rounded-full bg-amber/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-amber">
          Citations
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {sources.length === 0 ? (
          <div className="rounded-3xl bg-shell p-5 text-sm text-slate">
            Sources will appear here after retrieval-backed answers.
          </div>
        ) : (
          sources.map((source) => (
            <div key={source.chunk_id} className="rounded-3xl bg-shell p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-bold text-ink">{source.filename}</div>
                  <div className="mt-1 text-xs uppercase tracking-[0.18em] text-slate">
                    {source.page_number ? `Page ${source.page_number}` : 'Document-level metadata'}
                  </div>
                </div>
                <div className="mono text-xs text-accent">
                  score {Number(source.score).toFixed(3)}
                </div>
              </div>
              <p className="mt-3 text-sm leading-7 text-slate">{source.excerpt}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

