
## Budget Overview

**Target Budget:** **$75-100 USD** (5-person team, 12-week development cycle)  
**Cost per Member:** $15-20 per person  
**Strategy:** Use production-grade managed services, leverage local GPU, minimize cloud computing costs

---

## Itemized Cost Breakdown

| Category | Item | Unit Cost | Quantity | Total | Justification |
|----------|------|-----------|----------|-------|---------------|
| **Hardware** | | | | | |
| | Cloud GPU (AWS EC2) | $0.26/hour | 40-60 hours | **$10-15** | Primary: AWS EC2 g4dn.xlarge spot instances for CV training and testing; reliable and scalable |
| | Local GPU (Backup) | $0 | 1+ devices | **$0** | Backup: Team-owned NVIDIA GPU (GTX 1060 or better) if available; reduces cloud costs |
| | Development Machines | $0 | 5 | **$0** | Personal laptops (existing); 16GB RAM minimum, CPU inference supported |
| **Software & APIs** | | | | | |
| | LLM (Gemini API - Free Tier) | $0 | 1500 requests/day | **$0** | Primary: Google Gemini 1.5 Flash free tier; 15 RPM, 1M tokens/min, 1500 requests/day limit |
| | LLM (Groq API - Backup) | $0 | 100-200 calls | **$0** | Backup: Groq offers free tier for LLaMA 3 (6000 requests/day); use if local LLM insufficient |
| | LLM (OpenAI - Optional) | $0.01-0.03/call | 0-50 calls | **$0-1.50** | Optional: GPT-4o-mini for 10-20 complex bug reports only; budgeted if quality gap exists |
| | Database (Supabase Pro) | $25/month | 3 months | **$75** | Production tier: 8GB storage, 50GB bandwidth/month, dedicated resources, no inactivity pausing |
| | Database (PostgreSQL Local) | $0 | - | **$0** | Backup: Local PostgreSQL on development machines if needed |
| | VizDoom | $0 | - | **$0** | Open-source (MIT license) |
| | PyTorch | $0 | - | **$0** | Open-source (BSD license) |
| | Pre-trained DQN Agent (Arnold) | $0 | - | **$0** | Existing models from research repository |
| **Project Management** | | | | | |
| | Jira (Free Tier) | $0 | 5 users | **$0** | Up to 10 users free; sufficient for team task tracking |
| | GanttProject | $0 | - | **$0** | Open-source desktop application for Gantt charts |
| **Data & Resources** | | | | | |
| | CV Training Dataset | $0 | 500-750 frames | **$0** | Self-annotated; team labor distributed (3-4 hours per member) |
| | Test Maps (Doom WADs) | $0 | 50+ maps | **$0** | Community-created maps from idgames archive (freely available) |
| **Development Tools** | | | | | |
| | Flask/FastAPI | $0 | - | **$0** | Open-source Python frameworks |
| | React.js (Vite) | $0 | - | **$0** | Open-source frontend library with Vite build tool |
| | Git/GitHub | $0 | - | **$0** | Free tier (public repository, unlimited collaborators) |
| | VS Code / PyCharm | $0 | - | **$0** | Free community editions |
| | Google AI Studio (LLM) | $0 | - | **$0** | Free API access for Gemini models |
| **Collaboration** | | | | | |
| | Discord | $0 | - | **$0** | Free tier (unlimited messages, voice channels) |
| **Hosting & Deployment** | | | | | |
| | Frontend Hosting (Vercel) | $0 | - | **$0** | Free tier for React apps (100GB bandwidth/month) |
| | Backend Hosting (Render) | $0 | - | **$0** | Free tier for Flask API (750 hours/month) |
| | Domain Name (Optional) | $0-12 | 0-1 | **$0-12** | Optional .dev domain via Google Domains; not required for project |
| | SSL Certificate | $0 | - | **$0** | Let's Encrypt (free) or automatic via Vercel/Render |
| **Contingency** | | | | | |
| | Emergency Cloud GPU | - | - | **$0-20** | If local GPU fails or insufficient VRAM; AWS spot instances as backup |
| | LLM API Overage | - | - | **$0-10** | If Groq free tier exhausted and quality requires OpenAI calls |
| | Additional Storage | - | - | **$0-10** | Extra bandwidth or storage if exceeding Pro tier limits (unlikely) |
| **TOTAL (Expected)** | | | | **$85-90** | **Most likely outcome:** Supabase Pro + Cloud GPU + minimal additional costs |
| **TOTAL (Max Budget)** | | | | **$100** | **Worst-case scenario:** All contingencies triggered |

---

## Cost Optimization Strategy Summary

### GPU Usage (Cost: $10-15)
- **Primary:** AWS EC2 g4dn.xlarge spot instances ($0.26/hour, 40-60 hours for CV training)
- **Backup:** Local NVIDIA GPU if available (reduces cloud costs to $0)
- **Alternative:** Google Colab free tier (12 hours/day GPU access)

### LLM Integration (Target: $0)
- **Primary:** Google Gemini 1.5 Flash API (free tier: 1500 requests/day, sufficient for 150+ maps)
- **Backup:** Groq API free tier (6000 requests/day free) if Gemini limits exceeded
- **Optional:** OpenAI GPT-4o-mini for 10-20 critical bugs only ($0-1.50)

### Database Hosting (Cost: $75)
- **Primary:** Supabase Pro tier ($25/month × 3 months = $75)
  - 8GB storage (sufficient for 500+ maps)
  - 50GB bandwidth/month
  - No inactivity pausing (always accessible)
  - Dedicated resources for better performance
- **Backup:** Local PostgreSQL for development/testing

### File Storage (Target: $0-0.50)
- **Primary:** Supabase Storage (1GB included in free tier)
- **Alternative:** AWS S3 (5GB free tier, then $0.023/GB)
- **Backup:** GitHub Releases for screenshot archives

### Deployment & Hosting (Target: $0)
- **Frontend:** Vercel free tier (100GB bandwidth/month)
- **Backend:** Render free tier (750 hours/month) or Railway ($5 free credit/month)

---

## Recommended Technology Stack (Zero-Cost)

| Component | Technology | Cost |
|-----------|-----------|------|
| Database | Supabase Pro ($25/month × 3 months) | $75 |
| File Storage | Supabase Storage (1GB) | $0 |
| LLM | Google Gemini 1.5 Flash API (Free Tier) | $0 |
| GPU | AWS EC2 Spot Instances (40-60h) | $10-15 |
| Frontend Hosting | Vercel | $0 |
| Backend Hosting | Render | $0 |
| **Total Monthly Cost** | | **$25** |

---

## Final Budget Summary

| Scenario | Cost | Description |
|----------|------|-------------|
| **Optimal Path** | **$85** | Cloud GPU (AWS EC2) + Gemini API (free tier) + Supabase Pro + Vercel/Render hosting |
| **Likely Path** | **$85-90** | Supabase Pro + Cloud GPU (40-60h) + minor additional costs |
| **Contingency Path** | **$95-100** | Supabase Pro + Extended cloud GPU usage + Groq API backup + domain |
| **Maximum Budget** | **$100** | All contingencies triggered + optional domain + extended cloud GPU |
