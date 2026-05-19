const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

async function parseResponse(response) {
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Request failed')
  }
  return response.json()
}

function parseJsonResponse(text) {
  if (!text) {
    return {}
  }
  return JSON.parse(text)
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)
  return parseResponse(response)
}

export async function fetchStats() {
  const response = await fetch(`${API_BASE_URL}/documents/stats`)
  return parseResponse(response)
}

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`)
  return parseResponse(response)
}

export function uploadDocuments(files, tags, onProgress) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  formData.append('tags', tags)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}/documents/upload`, true)

    xhr.upload.onprogress = (event) => {
      if (typeof onProgress !== 'function') {
        return
      }
      if (!event.lengthComputable) {
        onProgress(0)
        return
      }
      onProgress(Math.round((event.loaded / event.total) * 100))
    }

    xhr.onerror = () => reject(new Error('Upload failed'))
    xhr.onload = () => {
      try {
        const response = parseJsonResponse(xhr.responseText)
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(response)
          return
        }
        reject(new Error(response?.detail || response?.message || xhr.responseText || 'Request failed'))
      } catch (error) {
        reject(error)
      }
    }

    xhr.send(formData)
  })
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
