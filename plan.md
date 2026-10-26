# ExpressDisplay - AI Lead Intelligence & Sourcing Platform Development Plan

## 1. Context & Business Objectives

**Client**: ExpressDisplay ([expressdisplay.net](https://expressdisplay.net/))  
**Core Business**: Sales and integration of dynamic digital signage, Smart Boards (interactive touchscreen displays), Ticket Kiosks & Queue Management Systems, Interactive & Window Totems, Stretch Screens (shelf-edge displays), and Video Walls (LED walls) in Tunisia and North Africa.

**Current Bottleneck**:  
The sales and marketing team spends hours every day manually searching websites on Google and social media, checking if prospects operate physical locations/branches, guessing their audiovisual needs, and hand-typing cold outreach messages.

**Mission**:  
Design, build, and deploy an **automated AI & scraping intelligence platform** that:
1. Automatically discovers target businesses with **complete source origin traceability (Provenance)**.
2. Analyzes their website content using **Google Gemini 1.5 Flash** to evaluate fit (0–100 score) and recommend the matching ExpressDisplay hardware/software solution.
3. Extracts contact details (phone, email, decision-maker) at zero extra cost.
4. Delivers a **Next.js dashboard hosted on Vercel** featuring sales pipeline status tracking (Mini-CRM) and 1-click outreach actions (WhatsApp pitch, Email direct, CSV export, Quick Add URL).

---

## 2. Chosen Technology Stack

* **Database & Realtime Backend**: **Supabase** (Managed PostgreSQL + Supabase Realtime + Row-Level Security).
* **Orchestration & Workflow Engine**: **n8n** (Automations, scheduled crons, HTTP requests, LLM chain nodes, database insertion).
* **Frontend Web Application**: **Next.js (App Router)** + Tailwind CSS + Lucide Icons, deployed on **Vercel**.
* **AI & Reasoning Engine**: **Google Gemini 1.5 Flash** (Content analysis, 0–100 fit scoring, product mapping, contact extraction, and personalized French pitch drafting).
* **Web Scraping & Extraction**: Native n8n HTTP Request node (zero third-party crawler API subscriptions) + Google Maps / Places scraper (Outscraper/Apify or Google Places API).
* **Contact Discovery**: 100% native and free (extracted directly by Gemini from the scraped website footer/contact page and Google Maps listing).

---

## 3. System Architecture

```
                    ┌──────────────────────────────────────────┐
                    │             Source Channels              │
                    │   - Google Maps (Clinics, Retail, etc.)  │
                    │   - Dashboard: "Quick Add URL" Button    │
                    └─────────────────────┬────────────────────┘
                                          │
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │               n8n Engine                 │
                    │ 1. Cron or Webhook Trigger               │
                    │ 2. Deduplication check via Supabase      │
                    │ 3. Native HTTP Request node (Fetch HTML) │
                    │ 4. Google Gemini 1.5 Flash Node:         │
                    │    - 0-100 Fit Scoring & Eligibility     │
                    │    - ExpressDisplay Product Matching     │
                    │    - Contact Extraction (Phone/Email)    │
                    │    - Tailored Sales Pitch Drafting       │
                    └─────────────────────┬────────────────────┘
                                          │
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │          Supabase (PostgreSQL)           │
                    │  Tables: 'leads', 'lead_provenance'      │
                    │  Supabase Realtime event publishing      │
                    └─────────────────────┬────────────────────┘
                                          │
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │         Next.js UI (on Vercel)           │
                    │  - Opportunity Feed with Provenance      │
                    │  - Origin & Product Line Filters         │
                    │  - Mini-CRM (New, Contacted, Won, Lost)  │
                    │  - 1-Click WhatsApp & Email Pre-filled   │
                    │  - Live "Quick Add URL" Modal            │
                    │  - 1-Click CSV Export                    │
                    └──────────────────────────────────────────┘
```

---

## 4. Database Schema (Supabase PostgreSQL SQL)

### Table: `leads`
```sql
CREATE TABLE public.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    website_url TEXT,
    sector TEXT,
    city TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    contact_person TEXT,
    contact_role TEXT,
    fit_score INT CHECK (fit_score >= 0 AND fit_score <= 100),
    matched_product TEXT NOT NULL,
    ai_rationale TEXT,
    generated_pitch TEXT,
    status TEXT DEFAULT 'NEW' CHECK (status IN ('NEW', 'CONTACTED', 'IN_DISCUSSION', 'WON', 'LOST')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

### Table: `lead_provenance` (Source Origin Tracking)
```sql
CREATE TABLE public.lead_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES public.leads(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('GOOGLE_MAPS', 'MANUAL_URL', 'DIRECTORY', 'WEB_CRAWL')),
    search_query TEXT,
    source_url TEXT,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

### Performance Indexes & Triggers
```sql
CREATE INDEX IF NOT EXISTS idx_leads_status ON public.leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_fit_score ON public.leads(fit_score DESC);
CREATE INDEX IF NOT EXISTS idx_lead_provenance_lead_id ON public.lead_provenance(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_provenance_source_type ON public.lead_provenance(source_type);

-- Automatic updated_at trigger
CREATE OR REPLACE FUNCTION public.set_current_timestamp_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_leads_updated_at ON public.leads;
CREATE TRIGGER trg_leads_updated_at
BEFORE UPDATE ON public.leads
FOR EACH ROW
EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- Unified View for Frontend Queries
CREATE OR REPLACE VIEW public.v_leads_with_provenance AS
SELECT 
    l.id,
    l.company_name,
    l.website_url,
    l.sector,
    l.city,
    l.address,
    l.phone,
    l.email,
    l.contact_person,
    l.contact_role,
    l.fit_score,
    l.matched_product,
    l.ai_rationale,
    l.generated_pitch,
    l.status,
    l.created_at,
    l.updated_at,
    p.source_type,
    p.search_query,
    p.source_url,
    p.captured_at
FROM public.leads l
LEFT JOIN public.lead_provenance p ON l.id = p.lead_id;

-- Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE public.leads;
ALTER PUBLICATION supabase_realtime ADD TABLE public.lead_provenance;
```

---

## 5. n8n Workflows Specification

### Workflow 1: Scheduled Batch Sourcing (Automated Prospecting)
1. **Schedule Trigger**: Runs on a cron schedule (e.g., Monday–Friday at 07:00 AM).
2. **Rotating Target Selector**: Dynamically picks a target sector and city in Tunisia (*e.g., Private Clinics in Tunis, Retail Chains in Ariana, Banks in Lac 2, Universities in Sousse*).
3. **Google Places / Maps Node**: Fetches up to 25 venues matching the query.
4. **Deduplication Check**: Queries Supabase to ignore domains that already exist.
5. **HTTP Request Node**: Fetches HTML from the homepage and contact page.
6. **Gemini 1.5 Flash Node**:
   * Evaluates business type and maps it to ExpressDisplay's 5 core product lines:
     * *Clinics / Banks / Healthcare* $\rightarrow$ **Ticket Kiosks & Queue Management**.
     * *Schools / Universities / Corporate HQs* $\rightarrow$ **75"/86" Interactive Smart Board**.
     * *Fashion / Boutiques / Supermarkets* $\rightarrow$ **High-Brightness Window Totems & Stretch Screens**.
     * *Flagship Halls / Showrooms / Facades* $\rightarrow$ **Video Wall & Outdoor LED**.
   * Outputs strict JSON: `fit_score`, `matched_product`, `ai_rationale`, `phone`, `email`, `contact_person`, and `generated_pitch`.
7. **Supabase Insert Node**: Saves the record in `leads` and logs the search query in `lead_provenance`.

### Workflow 2: On-Demand Qualification ("Quick Add URL")
1. **Webhook Node**: Receives a POST payload `{ "url": "https://target-company.tn" }` from the Next.js frontend.
2. **HTTP Request Node**: Fetches the website HTML.
3. **Gemini 1.5 Flash Node**: Analyzes and qualifies the company in 3–5 seconds.
4. **Supabase Insert Node**: Stores the lead with provenance set to `MANUAL_URL`.
5. **Respond to Webhook**: Returns the qualified JSON payload to the UI for immediate display.

---

## 6. Next.js Dashboard Specification (on Vercel)

1. **Origin & Provenance Badges**:
   * Every card prominently shows where it originated from (*e.g., `📍 Google Maps: "Cliniques Tunis"`, `🌐 Quick Add Manual`, `📒 B2B Directory`*) with a direct link to the original listing.
2. **Multi-Criteria Filtering**:
   * Filter by **Provenance Channel** (Google Maps vs. Manual Add).
   * Filter by **Target Product** (Smart Board, Ticket Kiosk, Totem, Video Wall, Stretch Screen).
   * Filter by **AI Fit Score** (High > 85%, Medium 70–85%).
   * Filter by **Pipeline Status** (New, Contacted, In Discussion, Won, Lost).
3. **Mini-CRM & 1-Click Action Suite**:
   * **WhatsApp Pitch Button**: Launches WhatsApp Web with the prospect's extracted phone number and the pre-written French pitch pre-filled.
   * **Email Direct Button**: Launches the email client (`mailto:`) with pre-filled subject line and message.
   * **Copy Pitch Button**: 1-click clipboard copy.
   * **Status Selector**: Instant inline update synchronized with Supabase.
4. **"Quick Add URL" Modal**:
   * Form allowing sales reps to paste any company URL found during daily browsing for instant AI qualification.
5. **CSV Export**:
   * 1-click export of filtered leads for sales meetings or spreadsheet reporting.

---

## 7. Project Roadmap & Implementation Milestones

| Milestone | Key Deliverables | Estimated Time |
|---|---|---|
| **Phase 1: Database & Supabase** | • Initialize Supabase project.<br>• Execute `schema.sql` (tables, constraints, views, indexes).<br>• Configure API keys (`NEXT_PUBLIC_SUPABASE_URL`, `ANON_KEY`). | Day 1 |
| **Phase 2: n8n Pipelines & AI Prompt** | • Import `workflow_quick_add_url.json` and `workflow_scheduled_harvest.json`.<br>• Configure Gemini 1.5 Flash API credentials in n8n.<br>• Configure Supabase Postgres credentials in n8n.<br>• Verify end-to-end webhook execution. | Days 2 – 3 |
| **Phase 3: Next.js Frontend (Vercel)** | • Build UI components (Header, Filters, LeadCard, LeadInspector, QuickAddModal).<br>• Connect Supabase Realtime client for live updates.<br>• Connect 1-click WhatsApp, Email, and CSV export handlers. | Days 3 – 5 |
| **Phase 4: Testing & Deployment** | • Deploy frontend to Vercel.<br>• Run test qualification on 50 real Tunisian business sites.<br>• Review AI pitch accuracy with ExpressDisplay sales reps.<br>• Team onboarding and handover. | Days 6 – 7 |

---

## 8. Estimated Operating Costs

* **Vercel**: **$0 / month** (Hobby plan is more than sufficient for internal sales team use).
* **Supabase**: **$0 / month** (Free tier covers 500 MB database and 50,000 monthly reads).
* **n8n**: **$0 / month** (if self-hosted on an internal server or a $4–$5/mo VPS) or $20/mo (n8n Cloud).
* **Google Gemini 1.5 Flash**: **< $1.00 / month** (Very cost-effective; only pennies for thousands of qualifications).
* **Google Maps Harvesting**: **$0 to $5 / month** (Free tier credits or low-cost Apify/Outscraper runs).
* **Total Estimated Cost**: **$0 to ~$10 / month**.
