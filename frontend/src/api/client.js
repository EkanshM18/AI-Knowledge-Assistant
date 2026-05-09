const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

async function parseResponse(response) {
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Request failed')
  }
  return response.json()
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)
  return parseResponse(response)
}

export async function fetchStats() {
  const response = await fetch(`${API_BASE_URL}/documents/stats`)
  return parseResponse(response)
}

export async function uploadDocuments(files, tags) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  formData.append('tags', tags)

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData
  })
  return parseResponse(response)
}

export async function sendMessage(payload) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  return parseResponse(response)
}

