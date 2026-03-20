'use client'

import { ProfileViewData } from '@/lib/api'

interface ProfileViewProps {
  data: ProfileViewData
  apiBaseUrl?: string
}

export default function ProfileView({ data, apiBaseUrl = '' }: ProfileViewProps) {
  return (
    <div className="border border-neutral-100 rounded-2xl p-5 my-2 bg-neutral-50/50">
      {/* Photos row */}
      {data.photos.length > 0 && (
        <div className="flex gap-2 mb-4">
          {data.photos.map((photo) => (
            <div key={photo.id} className="relative">
              <img
                src={`${apiBaseUrl}${photo.url}`}
                alt="Profile"
                className="w-20 h-20 object-cover rounded-xl"
              />
              {photo.vibe_tags && photo.vibe_tags.length > 0 && (
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent rounded-b-xl px-1.5 py-0.5">
                  <p className="text-[8px] text-white truncate">{photo.vibe_tags.join(', ')}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Basic info */}
      <div className="flex items-center gap-2 mb-3">
        {data.age && (
          <span className="text-xs font-medium text-neutral-600 bg-white border border-neutral-100 px-2 py-0.5 rounded-lg">
            {data.age} y.o.
          </span>
        )}
        {data.gender && (
          <span className="text-xs font-medium text-neutral-600 bg-white border border-neutral-100 px-2 py-0.5 rounded-lg">
            {data.gender}
          </span>
        )}
      </div>

      {/* Vibe tags */}
      {data.vibe_tags && data.vibe_tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {data.vibe_tags.map((tag) => (
            <span
              key={tag}
              className="text-[10px] font-medium px-2 py-0.5 rounded-full"
              style={{ backgroundColor: '#FDB81320', color: '#B8860B' }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Profile sections */}
      <div className="space-y-2">
        {data.communication_style && (
          <div>
            <p className="text-[10px] text-neutral-400 uppercase tracking-wide mb-0.5">Communication</p>
            <p className="text-xs text-neutral-700">{data.communication_style}</p>
          </div>
        )}
        {data.values && (
          <div>
            <p className="text-[10px] text-neutral-400 uppercase tracking-wide mb-0.5">Values</p>
            <p className="text-xs text-neutral-700">{data.values}</p>
          </div>
        )}
        {data.partner_preferences && (
          <div>
            <p className="text-[10px] text-neutral-400 uppercase tracking-wide mb-0.5">Looking for</p>
            <p className="text-xs text-neutral-700">{data.partner_preferences}</p>
          </div>
        )}
      </div>
    </div>
  )
}
