# Uncle Kerja — 5-Minute Demo Script

> Screen recording walkthrough. Total runtime: ~5 minutes.
> Tip: run the backend and have a sample PDF resume + job description ready before you start.

---

## [0:00 – 0:45] Opening — What is Uncle Kerja?

**Show:** Landing page at `localhost:3000`

> "This is Uncle Kerja — an AI-powered career assistant built specifically for Malaysian job seekers.
> The idea is simple: upload your resume, paste a job description, and in about 90 seconds you get
> everything you need — a score, honest feedback, a fix plan, and real Malaysian job matches."

Scroll slowly down the landing page to show:
- The hero tagline and CTA buttons
- The 6 agent mascot cards

> "Under the hood, seven specialised AI agents run one after another, each handling one job.
> Let me show you who they are."

Point to each mascot card as you mention them:

1. **Parser Agent** — "Reads your resume and extracts a structured profile: skills, experience, education."
2. **Scorer Agent** — "Scores your profile against the job description across four dimensions — skills, experience, education, and ATS keywords — and gives you a number out of 100."
3. **Roaster Agent** — "Gives you the kind of honest feedback a senior recruiter would. No fluff, no feel-good noise."
4. **Coach Agent** — "Turns your gaps into a ranked 6-week action plan, including HRDF-claimable courses you can claim as a Malaysian worker."
5. **Job Finder** — "Searches Google Jobs live and returns real Malaysian listings with apply links — posted this week."
6. **Email Agent** — "Drafts bilingual cover letters in English and Bahasa Malaysia, and sends daily job alerts to your inbox."
7. **Reply Agent** — "The autonomous one. Reads your email replies and responds intelligently. Reply 'find me jobs in Penang' — it updates your search without you logging in."

---

## [0:45 – 1:15] Architecture in 30 Seconds

**Show:** Open a terminal or show a simple slide/diagram (the ASCII diagram from the README works well as a screenshot)

> "The architecture is a sequential agent pipeline on a FastAPI backend.
> Parser feeds into Scorer. Scorer feeds into both the Roaster and Job Finder in parallel.
> Everything merges in the Orchestrator, saves to Supabase, and the Email Agent sends alerts via AgentMail.
>
> The GLM-5.1 model from Z AI powers all the language tasks.
> We run agents sequentially — not in parallel — so we never overload the API mid-demo.
>
> The Reply Agent runs on a 5-minute scheduler. It reads the AgentMail inbox, classifies intent with GLM,
> and replies in the same email thread. Fully autonomous."

---

## [1:15 – 2:30] Core Flow — Analyse a Resume

**Show:** Navigate to `/analyse`

> "Let's run it live."

1. **Upload** a PDF resume (drag and drop into the drop zone)
2. **Paste** a real Malaysian job description into the text area (software engineer or data role works well)
3. Optionally add an email for job alerts
4. Click **Analyse Resume**

> "The pipeline is running now. You can see the progress bar tracking through each agent phase."

Point to the progress steps as they light up green.

> "Parser first — extracting the profile. Then Scorer against the job description. Then Roaster and Coach in parallel with Job Finder. About 90 seconds total."

Wait for the redirect to `/results/:id`.

---

## [2:30 – 3:30] Results — Walking Through the Tabs

**Show:** Results page, tab through Score → Roast → Action Plan → Jobs

### Score tab (20 sec)
> "Score tab. Overall fit out of 100, broken down by the four dimensions.
> Matched and missing skills are shown as tags. Any missing ATS keywords the recruiter's system
> would filter out are flagged in amber."

### Roast tab (20 sec)
> "Roast tab. This is the honest feedback. Skills assessment, experience review, presentation critique.
> And the silver lining — it always finds something genuine to say.
> The closing line is the Uncle Kerja signature."

### Action Plan tab (20 sec)
> "Action Plan. Ranked by impact. Each action has an effort estimate and specific resources —
> including HRDF-claimable courses for Malaysian workers."

### Jobs tab (20 sec)
> "Jobs tab. Live listings from Google Jobs, filtered for Malaysia.
> Match score for each job against this specific resume.
> Click Apply — takes you directly to the job posting.
> Click Cover Letter — GLM generates a bilingual cover letter in seconds."

**Demo the Cover Letter** — click Cover Letter on one job, switch between English and Bahasa Malaysia tabs.

---

## [3:30 – 4:15] Email Alerts + Inbox

**Show:** Navigate to `/alerts` (log in first as `teamusm20+user@gmail.com` / `User@1234`)

> "Job Alerts page. A user subscribes with their email and gets a welcome message from usm.z.ai@agentmail.to.
> From then on, daily job matches arrive in their inbox."

Show the "Job Alerts Sent to You" section.

> "This inbox only shows emails sent TO this specific user — their personal job alert history.
> Sent from the agent's AgentMail address, not a Gmail."

**Show:** Log in as admin (`tomleeatwork+Admin@gmail.com` / `Admin@1234`) and navigate to `/admin`

> "The admin panel shows the full AgentMail inbox — all inbound replies from all users.
> This is where the Reply Agent's work is visible.
> You can also manually trigger the Reply Agent here with 'Process inbox now'."

Point to health status (🟢 OK), AgentMail configured, DB stats.

---

## [4:15 – 5:00] History + Closing

**Show:** Navigate to `/history`

> "History page. Every analysis is persisted in Supabase — so you can come back later,
> compare results across different job applications, or share a session link."

Click **View** on an analysis to go back to the full results.

> "And that's Uncle Kerja. Seven AI agents. One Malaysian career copilot.
>
> Resume scored. Gaps identified. Action plan built. Live jobs found.
> Cover letters drafted in two languages. Daily alerts to your inbox.
> And when you reply to that email, the system responds — autonomously — in the same thread.
>
> Built in 30 hours at UMhack. Powered by Z AI GLM-5.1."

**End on the landing page or the results page with a strong score showing.**

---

## Tips for a Smooth Recording

- Have a real resume PDF ready (any tech/engineering CV works)
- Copy a real Malaysian job posting from JobStreet — paste the full JD
- Pre-warm the backend 10 minutes before recording so the first run isn't cold
- Demo accounts are hardcoded — they work even if Supabase is slow
- The Cover Letter modal is a great visual moment — use it
- If the analysis takes longer than 90s, narrate through it casually ("GLM is doing the heavy lifting here...")
