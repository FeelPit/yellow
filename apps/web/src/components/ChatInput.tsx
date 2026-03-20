'use client'

import { useState, useRef, FormEvent } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  onPhotoUpload?: (file: File) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, onPhotoUpload, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage('')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && onPhotoUpload) {
      onPhotoUpload(file)
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      {onPhotoUpload && (
        <div
          className={`relative shrink-0 w-11 h-11 rounded-xl flex items-center justify-center border border-neutral-200 bg-white transition-all hover:bg-neutral-50 active:scale-95 ${disabled ? 'opacity-30 pointer-events-none' : ''}`}
          data-testid="camera-button"
          title="Upload photo"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            disabled={disabled}
            data-testid="photo-file-input"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <svg className="pointer-events-none" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </svg>
        </div>
      )}
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
        className="flex-1 h-11 px-4 bg-neutral-50 border border-neutral-200 rounded-xl text-sm text-neutral-900 placeholder:text-neutral-400 outline-none transition-colors focus:border-neutral-400 focus:bg-white disabled:opacity-50"
        data-testid="chat-input"
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className="shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 hover:brightness-105 active:scale-95 disabled:opacity-30 disabled:pointer-events-none"
        style={{ backgroundColor: '#FDB813' }}
        data-testid="send-button"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </form>
  )
}
