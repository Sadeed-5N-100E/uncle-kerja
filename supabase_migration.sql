-- Uncle Kerja — Supabase Migration
-- Run this once in Supabase Dashboard → SQL Editor
-- https://supabase.com/dashboard/project/qlegqgnmethvuainkfmj/sql/new

-- ── 1. analyses ───────────────────────────────────────────────────────────────
-- Stores every resume analysis session.
CREATE TABLE IF NOT EXISTS public.analyses (
    id              TEXT PRIMARY KEY,           -- session UUID from orchestrator
    user_email      TEXT NOT NULL DEFAULT 'anonymous',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    job_title       TEXT,                       -- first line of the job description
    overall_score   INTEGER,                    -- 0-100
    verdict         TEXT,                       -- Strong Fit / Partial Fit / etc.
    summary         TEXT,                       -- one_line_summary from scorer
    roast_opening   TEXT,                       -- first line of roast (for history card)
    skills_matched  JSONB DEFAULT '[]',         -- list of matched skill strings
    jobs_count      INTEGER DEFAULT 0,
    errors          JSONB DEFAULT '[]',
    score_json      JSONB,                      -- full ScoreReport
    profile_json    JSONB                       -- full ResumeProfile
);

CREATE INDEX IF NOT EXISTS idx_analyses_user  ON public.analyses(user_email);
CREATE INDEX IF NOT EXISTS idx_analyses_time  ON public.analyses(created_at DESC);

-- ── 2. job_alerts ─────────────────────────────────────────────────────────────
-- One row per alert subscriber.
CREATE TABLE IF NOT EXISTS public.job_alerts (
    user_email      TEXT PRIMARY KEY,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    subscribed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_sent_at    TIMESTAMPTZ,
    last_session_id TEXT                        -- most recent analysis session
);

-- ── 3. sent_emails ────────────────────────────────────────────────────────────
-- Log of every outbound job alert email (survives server restarts).
CREATE TABLE IF NOT EXISTS public.sent_emails (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    to_email    TEXT NOT NULL,
    subject     TEXT NOT NULL,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    thread_id   TEXT,
    message_id  TEXT,
    email_type  TEXT NOT NULL DEFAULT 'job_alert'
                CHECK (email_type IN ('job_alert','welcome','cover_letter'))
);

CREATE INDEX IF NOT EXISTS idx_sent_to   ON public.sent_emails(to_email);
CREATE INDEX IF NOT EXISTS idx_sent_time ON public.sent_emails(sent_at DESC);

-- ── Row Level Security ────────────────────────────────────────────────────────
-- Backend uses service_role key → bypasses RLS automatically.
-- Enable RLS so anon/public key cannot read raw data.
ALTER TABLE public.analyses    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_alerts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sent_emails ENABLE ROW LEVEL SECURITY;

-- Service role bypass (implicit — no explicit policy needed for service_role).
-- Optional: allow users to read their own rows via JWT (not used in current build).
-- CREATE POLICY "users_own_analyses" ON public.analyses
--   FOR SELECT USING (auth.jwt() ->> 'email' = user_email);
