import { useState, useEffect } from 'react'
import { X, Copy, Check, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

export default function CoverLetterModal({ sessionId, jobIndex, jobTitle, company, onClose }) {
  const [data,    setData]    = useState(null)
  const [tab,     setTab]     = useState('en')
  const [loading, setLoading] = useState(true)
  const [copied,  setCopied]  = useState(false)

  useEffect(() => {
    api.coverLetter(sessionId, jobIndex)
      .then(setData)
      .catch(e => setData({ error: e.message }))
      .finally(() => setLoading(false))
  }, [sessionId, jobIndex])

  const copyText = async () => {
    const text = tab === 'en' ? data?.body_en : data?.body_ms
    if (!text) return
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-100 shrink-0">
          <div>
            <h3 className="font-semibold text-slate-900">Cover Letter</h3>
            <p className="text-xs text-slate-400 mt-0.5">{jobTitle} · {company}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 size={24} className="animate-spin text-blue-500 mr-2" />
            <span className="text-slate-400">Generating cover letter…</span>
          </div>
        ) : data?.error ? (
          <div className="flex-1 flex items-center justify-center p-8 text-red-500">{data.error}</div>
        ) : (
          <>
            {/* Tabs */}
            <div className="flex gap-1 p-4 pb-0 border-b border-slate-100 shrink-0">
              {[['en', 'English'], ['ms', 'Bahasa Malaysia']].map(([k, label]) => (
                <button key={k} onClick={() => setTab(k)}
                  className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2 -mb-px
                    ${tab === k ? 'border-blue-500 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
                  {label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-5">
              {tab === 'en' ? (
                <>
                  {data.subject_en && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm text-slate-600 mb-4">
                      <span className="font-medium text-slate-400 text-xs">Subject: </span>{data.subject_en}
                    </div>
                  )}
                  <pre className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed font-sans">
                    {data.body_en}
                  </pre>
                </>
              ) : (
                <>
                  {data.subject_ms && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm text-slate-600 mb-4">
                      <span className="font-medium text-slate-400 text-xs">Subjek: </span>{data.subject_ms}
                    </div>
                  )}
                  <pre className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed font-sans">
                    {data.body_ms}
                  </pre>
                </>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-100 shrink-0">
              <button onClick={copyText}
                className="flex items-center gap-2 w-full justify-center border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm py-2 rounded-lg transition-colors">
                {copied ? <><Check size={14} className="text-green-500" /> Copied!</> : <><Copy size={14} /> Copy to clipboard</>}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
