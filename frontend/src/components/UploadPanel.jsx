import { useMemo, useRef, useState } from 'react'

function formatDocumentStatus(status) {
  const normalized = status ?? 'queued'
  return normalized.replaceAll('_', ' ')
}

function statusTone(status) {
  switch (status) {
    case 'completed':
      return 'bg-accent/10 text-accent border-accent/30'
    case 'processing':
    case 'uploading':
    case 'queued':
      return 'bg-amber/10 text-amber border-amber/30'
    case 'failed':
      return 'bg-coral/10 text-coral border-coral/30'
    default:
      return 'bg-slate-100 text-slate border-mist'
  }
}

export function UploadPanel({ onUpload, uploading, uploadProgress, documents = [] }) {
  const [tags, setTags] = useState('')
  const [files, setFiles] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const selectedLabel = useMemo(() => {
    if (!files.length) return 'No files selected yet'
    if (files.length === 1) return files[0].name
    return `${files.length} files ready for upload`
  }, [files])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!files.length || uploading) {
      return
    }

    await onUpload(files, tags)
    setFiles([])
    setTags('')
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  function handleFileChange(event) {
    setFiles(Array.from(event.target.files ?? []))
  }

  function handleDrop(event) {
    event.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(event.dataTransfer.files ?? [])
    if (droppedFiles.length) {
      setFiles(droppedFiles)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-panel backdrop-blur"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-ink">Document Ingestion</h2>
          <p className="mt-2 max-w-xl text-sm text-slate">
            Upload enterprise knowledge assets to Supabase Storage. Metadata is saved in PostgreSQL and ingestion
            runs asynchronously in the backend.
          </p>
        </div>
        <div className="rounded-full bg-accent/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-accent">
          Supabase
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.4fr,1fr]">
        <div
          onDragEnter={() => setIsDragging(true)}
          onDragLeave={() => setIsDragging(false)}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
          className={[
            'rounded-3xl border border-dashed p-5 text-sm transition',
            isDragging ? 'border-ink bg-shell shadow-panel' : 'border-accent/35 bg-shell text-slate'
          ].join(' ')}
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <span className="block font-semibold text-ink">Drag and drop files here</span>
              <span className="mt-1 block">PDF, TXT, DOCX, Markdown, CSV, JSON, HTML</span>
            </div>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="rounded-full border border-ink bg-white px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-ink transition hover:bg-ink hover:text-white"
            >
              Browse
            </button>
          </div>

          <input
            ref={inputRef}
            type="file"
            multiple
            className="sr-only"
            onChange={handleFileChange}
          />

          <div className="mt-4 rounded-2xl border border-white/70 bg-white/80 px-4 py-3 text-sm text-slate">
            {selectedLabel}
          </div>

          {uploading && (
            <div className="mt-4">
              <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.18em] text-slate">
                <span>Upload progress</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full border border-ink bg-white">
                <div
                  className="h-full bg-ink transition-all duration-300"
                  style={{ width: `${Math.max(uploadProgress, 4)}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-slate">
                Files are being sent to Supabase Storage, then ingestion is triggered in the background.
              </p>
            </div>
          )}
        </div>

        <label className="rounded-3xl bg-shell p-5 text-sm text-slate">
          <span className="block font-semibold text-ink">Tags</span>
          <span className="mt-1 block">Comma-separated metadata for future filtering.</span>
          <input
            type="text"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            placeholder="finance, hr, onboarding"
            className="mt-4 w-full rounded-2xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-accent"
          />
        </label>
      </div>

      <div className="mt-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="text-sm text-slate">{selectedLabel}</div>
        <button
          type="submit"
          disabled={!files.length || uploading}
          className="rounded-full bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? 'Uploading...' : 'Upload to Supabase'}
        </button>
      </div>

      <div className="mt-6 rounded-[1.8rem] border border-white/70 bg-shell p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-extrabold uppercase tracking-[0.18em] text-ink">
              Ingestion Status
            </h3>
            <p className="mt-2 text-sm text-slate">
              Latest documents are pulled from PostgreSQL metadata and updated as ingestion progresses.
            </p>
          </div>
          <div className="rounded-full bg-ink px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-white">
            {documents.length} files
          </div>
        </div>

        <div className="mt-4 grid gap-3">
          {documents.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-mist bg-white px-4 py-4 text-sm text-slate">
              No uploaded documents yet.
            </div>
          ) : (
            documents.slice(0, 5).map((document) => (
              <div key={document.id} className="rounded-2xl border border-white/70 bg-white px-4 py-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="font-bold text-ink">{document.filename}</div>
                    <div className="mt-1 text-xs uppercase tracking-[0.16em] text-slate">
                      {document.file_type} · {document.vector_collection ?? 'pending collection'}
                    </div>
                  </div>
                  <div className={`rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] ${statusTone(document.ingestion_status)}`}>
                    {formatDocumentStatus(document.ingestion_status)}
                  </div>
                </div>

                <div className="mt-3 grid gap-2 text-sm text-slate sm:grid-cols-2">
                  <div>Chunks: {document.chunk_count ?? 0}</div>
                  <div>Vectors: {document.vector_count ?? 0}</div>
                  <div className="sm:col-span-2">
                    Storage path: <span className="mono break-all">{document.storage_path}</span>
                  </div>
                </div>

                {document.error_message && (
                  <div className="mt-3 rounded-2xl border border-coral/30 bg-coral/10 px-3 py-2 text-sm text-coral">
                    {document.error_message}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </form>
  )
}
