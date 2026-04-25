import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, ChevronRight, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

export default function Dashboard() {
  const navigate = useNavigate()
  const [file,    setFile]    = useState(null)
  const [jd,      setJd]      = useState('')
  const [email,   setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState({ step: '', pct: 0 })
  const [error,   setError]   = useState('')

  const onDrop = useCallback(accepted => {
    if (accepted[0]) setFile(accepted[0])
  }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'] }, maxFiles: 1,
  })

  const STEPS = [
    { key: 'parse',  label: 'Parsing resume',                pct: 20 },
    { key: 'score',  label: 'Scoring against job description', pct: 45 },
    { key: 'roast',  label: 'Roasting + coaching + job search (parallel)', pct: 85 },
    { key: 'done',   label: 'Done!',                          pct: 100 },
  ]

  const submit = async (e) => {
    e.preventDefault()
    if (!jd.trim()) return setError('Paste the job description.')
    if (!file && !document.getElementById('resume-paste')?.value?.trim())
      return setError('Upload a PDF or paste resume text.')
    setError(''); setLoading(true)

    const fd = new FormData()
    fd.append('job_description', jd)
    if (email.trim()) fd.append('alert_email', email.trim())
    if (file) {
      fd.append('resume_file', file)
    } else {
      fd.append('resume_text', document.getElementById('resume-paste').value)
    }

    // Animate steps while waiting for response
    let stepIdx = 0
    const interval = setInterval(() => {
      if (stepIdx < STEPS.length - 1) {
        setProgress(STEPS[stepIdx])
        stepIdx++
      }
    }, 22000) // ~22s per agent phase

    try {
      const session = await api.analyze(fd)
      clearInterval(interval)
      setProgress(STEPS[STEPS.length - 1])
      setTimeout(() => navigate(`/results/${session.session_id}`), 500)
    } catch (err) {
      clearInterval(interval)
      setError(err.message)
      setLoading(false)
      setProgress({ step: '', pct: 0 })
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 page-enter">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Analyse your resume</h1>
        <p className="text-slate-500 mt-1">Upload your resume and a job description. We'll score, roast, coach, and find matching jobs.</p>
      </div>

      {loading ? (
        /* Progress state */
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center">
          <Loader2 size={40} className="animate-spin text-blue-500 mx-auto mb-4" />
          <p className="font-semibold text-slate-800 text-lg mb-1">{progress.step || 'Starting agents…'}</p>
          <p className="text-slate-400 text-sm mb-6">This takes about 90 seconds. Agents run in parallel.</p>
          <div className="max-w-xs mx-auto">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Progress</span><span>{progress.pct}%</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full bar-animate" style={{ width: `${progress.pct}%` }} />
            </div>
          </div>
          <div className="mt-6 space-y-2">
            {STEPS.map((s, i) => (
              <div key={s.key} className={`flex items-center gap-2 text-sm transition-colors
                ${progress.pct >= s.pct ? 'text-green-600' : 'text-slate-300'}`}>
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold
                  ${progress.pct >= s.pct ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-300'}`}>
                  {progress.pct >= s.pct ? '✓' : i + 1}
                </div>
                {s.label}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-5">
          {/* Drop zone */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Resume (PDF)</label>
            <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}>
              <input {...getInputProps()} />
              {file ? (
                <div className="flex items-center justify-center gap-3">
                  <FileText size={20} className="text-blue-500" />
                  <span className="text-sm font-medium text-slate-700">{file.name}</span>
                  <button type="button" onClick={e => { e.stopPropagation(); setFile(null) }}
                    className="text-slate-400 hover:text-red-500"><X size={16} /></button>
                </div>
              ) : (
                <>
                  <Upload size={24} className="text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">
                    <span className="text-blue-600 font-medium">Click to upload</span> or drag & drop
                  </p>
                  <p className="text-xs text-slate-400 mt-1">PDF or TXT</p>
                </>
              )}
            </div>
          </div>

          {/* Or paste */}
          {!file && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Or paste resume text</label>
              <textarea id="resume-paste" rows={5}
                placeholder="Paste your full resume text here…"
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
            </div>
          )}

          {/* Job description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Job Description <span className="text-red-500">*</span>
            </label>
            <textarea value={jd} onChange={e => setJd(e.target.value)} rows={8}
              placeholder="Paste the full job description here…"
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
          </div>

          {/* Email for alerts */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Email for job alerts <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-xl">{error}</div>
          )}

          <button type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
            Analyse Resume <ChevronRight size={18} />
          </button>
        </form>
      )}
    </div>
  )
}
