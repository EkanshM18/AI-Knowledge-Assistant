import { useState } from 'react'

export function UploadPanel({ onUpload, uploading }) {
  const [tags, setTags] = useState('')
  const [files, setFiles] = useState([])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!files.length || uploading) {
      return
    }
    await onUpload(files, tags)
    setFiles([])
    setTags('')
    event.target.reset()
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
            Upload enterprise knowledge assets and index them into local Qdrant with embeddings and metadata.
          </p>
        </div>
        <div className="rounded-full bg-accent/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-accent">
          Local RAG
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.4fr,1fr]">
        <label className="rounded-3xl border border-dashed border-accent/35 bg-shell p-5 text-sm text-slate">
          <span className="block font-semibold text-ink">Choose files</span>
          <span className="mt-1 block">PDF, TXT, DOCX, Markdown, CSV, JSON, HTML</span>
          <input
            type="file"
            multiple
            className="mt-4 block w-full text-sm"
            onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          />
        </label>

        <label className="rounded-3xl bg-shell p-5 text-sm text-slate">
          <span className="block font-semibold text-ink">Tags</span>
          <span className="mt-1 block">Comma-separated metadata for filtering later.</span>
          <input
            type="text"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            placeholder="finance, hr, onboarding"
            className="mt-4 w-full rounded-2xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-accent"
          />
        </label>
      </div>

      <div className="mt-5 flex items-center justify-between gap-4">
        <div className="text-sm text-slate">
          {files.length ? `${files.length} file(s) ready for ingestion` : 'No files selected yet'}
        </div>
        <button
          type="submit"
          disabled={!files.length || uploading}
          className="rounded-full bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? 'Indexing...' : 'Upload and Index'}
        </button>
      </div>
    </form>
  )
}

