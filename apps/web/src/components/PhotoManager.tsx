'use client'

import { useState, useEffect, useRef } from 'react'
import { apiClient, PhotoResponse } from '@/lib/api'

interface PhotoManagerProps {
  isOpen: boolean
  onClose: () => void
  onPhotoChange?: () => void
}

export default function PhotoManager({ isOpen, onClose, onPhotoChange }: PhotoManagerProps) {
  const [photos, setPhotos] = useState<PhotoResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isOpen) loadPhotos()
  }, [isOpen])

  const loadPhotos = async () => {
    setLoading(true)
    try {
      const data = await apiClient.getPhotos()
      setPhotos(data)
    } catch {
      setError('Failed to load photos')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError(null)
    try {
      await apiClient.uploadPhoto(file)
      await loadPhotos()
      onPhotoChange?.()
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDelete = async (photoId: string) => {
    try {
      await apiClient.deletePhoto(photoId)
      setPhotos((prev) => prev.filter((p) => p.id !== photoId))
      onPhotoChange?.()
    } catch {
      setError('Failed to delete photo')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-2xl w-full max-w-md mx-4 overflow-hidden shadow-xl">
        <div className="px-5 py-4 flex items-center justify-between border-b border-neutral-100">
          <h2 className="text-sm font-semibold text-neutral-900">Your Photos</h2>
          <button
            onClick={onClose}
            className="text-neutral-400 hover:text-neutral-600 text-lg leading-none"
          >
            &times;
          </button>
        </div>

        <div className="p-5">
          {error && (
            <p className="text-xs text-red-500 mb-3">{error}</p>
          )}

          {loading ? (
            <div className="flex justify-center py-8">
              <div
                className="w-6 h-6 rounded-full border-2 border-t-transparent animate-spin"
                style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
              />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-3 gap-3 mb-4">
                {photos.map((photo) => (
                  <div key={photo.id} className="relative group aspect-square">
                    <img
                      src={apiClient.getPhotoUrl(photo.id)}
                      alt={photo.original_name}
                      className="w-full h-full object-cover rounded-xl"
                    />
                    <button
                      onClick={() => handleDelete(photo.id)}
                      className="absolute top-1.5 right-1.5 w-6 h-6 rounded-full bg-black/50 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      &times;
                    </button>
                    {photo.vibe_tags && photo.vibe_tags.length > 0 && (
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent rounded-b-xl px-2 py-1.5">
                        <p className="text-[10px] text-white truncate">
                          {photo.vibe_tags.join(', ')}
                        </p>
                      </div>
                    )}
                  </div>
                ))}

                {photos.length < 3 && (
                  <label className="aspect-square border-2 border-dashed border-neutral-200 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-neutral-300 transition-colors">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png"
                      className="hidden"
                      onChange={handleUpload}
                      disabled={uploading}
                    />
                    {uploading ? (
                      <div
                        className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin"
                        style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
                      />
                    ) : (
                      <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ccc" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="12" y1="5" x2="12" y2="19" />
                          <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                        <span className="text-[10px] text-neutral-400 mt-1">Add</span>
                      </>
                    )}
                  </label>
                )}
              </div>

              <p className="text-[10px] text-neutral-400 text-center">
                {photos.length}/3 photos &middot; JPEG or PNG, max 5MB
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
