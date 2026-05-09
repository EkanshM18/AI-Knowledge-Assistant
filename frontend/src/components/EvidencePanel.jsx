export function EvidencePanel({ bot, sources, toolCalls, route }) {
  const isEnterprise = bot === 'enterprise'

  return (
    <div className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-panel backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-extrabold text-ink">
            {isEnterprise ? 'Grounding Sources' : 'Tool Activity'}
          </h2>
          <p className="mt-2 text-sm text-slate">
            {isEnterprise
              ? 'Retrieved evidence used to generate the latest enterprise answer.'
              : 'General assistant tools invoked to answer the latest request.'}
          </p>
        </div>
        <div className="rounded-full bg-amber/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-amber">
          {route || 'idle'}
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {isEnterprise ? (
          sources.length === 0 ? (
            <div className="rounded-3xl bg-shell p-5 text-sm text-slate">
              Citations will appear here after enterprise retrieval-backed answers.
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
          )
        ) : toolCalls.length === 0 ? (
          <div className="rounded-3xl bg-shell p-5 text-sm text-slate">
            Tool usage will appear here after weather, news, joke, or time requests.
          </div>
        ) : (
          toolCalls.map((tool, index) => (
            <div key={`${tool.tool_name}-${index}`} className="rounded-3xl bg-shell p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-bold capitalize text-ink">{tool.tool_name}</div>
                  <div className="mt-1 text-xs uppercase tracking-[0.18em] text-slate">
                    {tool.source_label || 'General assistant tool'}
                  </div>
                </div>
                <div
                  className={[
                    'rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.2em]',
                    tool.status === 'success'
                      ? 'bg-accent/10 text-accent'
                      : tool.status === 'error'
                        ? 'bg-coral/10 text-coral'
                        : 'bg-amber/10 text-amber'
                  ].join(' ')}
                >
                  {tool.status}
                </div>
              </div>
              <p className="mt-3 text-sm leading-7 text-slate">{tool.summary}</p>
              {tool.source_url && (
                <a
                  href={tool.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-flex text-sm font-semibold text-accent hover:text-ink"
                >
                  Open source
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

