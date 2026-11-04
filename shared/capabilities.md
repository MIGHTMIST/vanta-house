# What works here, what doesn't, and how to fix it

Checked from this cloud workspace on **4 Nov 2026**. "Checked" = I ran it today. "Not tested" = the tool is
there but I did not run it. Every bot reads this before promising anything.

---

## ✅ Works now

| What | Status | Used for |
|---|---|---|
| Vanta Team Room + old Lab board (read/write rows) | checked | orders, status cards, log, John questions |
| Cloudflare: list workers, read bot code, query the bot database (D1) | checked (workers list) | reading chats and leads, finding bot bugs, writing new bot versions |
| Google Drive | checked ("100 books" folder) | reading playbooks, saving papers |
| Google Docs, Sheets, Slides, Gmail, Calendar | connected, not tested | packs, trackers, family books data, email drafts, calendar |
| Canva, fal.ai, Higgsfield connectors | connected, not tested (they cost credits) | designs, AI images and video |
| Video and image work: ffmpeg, ImageMagick, Python, Node, headless Chrome (for code-made videos and HTML → PDF) | checked (installed) | reels, ads, motion graphics, PDFs |
| Web search | tool available, not tested | research |
| Publishing pages (artifacts), PDFs, docs | available | packs, dashboards, reports |
| Head chat talking to the three bot chats directly | tools available, not tested (`create_session`, `send_message`, `list_events`) | no more carrying questions between chats by hand |

## ⛔ Blocked now and why

### A. The open internet is switched off for this workspace
Tested, refused: `facebook.com`, `graph.facebook.com`, `business.facebook.com`, `tiktok.com`, `google.com`,
`youtube.com`, `web.whatsapp.com`, `api.cloudflare.com`, `v3b.fal.media`.

**Fix (free, 1 minute, Abdullahi):** in this cloud environment's settings (environment menu in the session title
bar → Edit → Network access), choose **Full**, or add those domains under Allowed domains and keep
"Allow package managers" ticked. Steps: https://code.claude.com/docs/en/cloud-environments#network-access
A new session picks it up.

### B. No logged-in browser here
In Cowork / the desktop app, Claude clicked in **your** Chrome (Claude in Chrome) or on **your** screen (computer use).
A cloud session has neither, so it cannot open Meta Business Suite, Ads Manager, Facebook groups, TikTok Studio,
Google Business Profile, WhatsApp Web, the Drive viewer for scanned PDFs, or the Apps Script editor.

**Fix 1: use official APIs instead of clicks (free, after fix A).** Most of your clicking work has an API:

| Your job (skill) | API that replaces the clicks | Cost |
|---|---|---|
| Post or schedule a Reel on the Burhan 2 / Vanta Page (`facebook-reel-posting`) | Meta Graph API, Page `video_reels` | free |
| Read Page and post numbers (Post tracker) | Meta Graph API, Page and video insights | free |
| Read Ads Manager numbers (`ad-warning`, market research step 1) | Meta Marketing API, `ads_read` | free |
| Boost a post (`facebook-boost-post`) | Meta Marketing API: an ad made from the existing post | free (you pay only the ad money, and only after you say yes) |
| Instagram posts | Instagram Graph API (business account) | free |
| WhatsApp bot (`whatsapp-cloud-api-bot-setup`) | WhatsApp Cloud API (already used by the bot) | replies inside 24 hours are free; some template messages are paid (check Meta's pricing page) |
| YouTube comment research (Marketing research step 4) | YouTube Data API key | free, 10,000 units a day |
| Deploy a new bot version (today: you paste it into Cloudflare) | Cloudflare API token + `wrangler deploy`, old version kept for rollback | free plan: 100,000 bot requests a day |
| Family books (`family-books`) | Google Sheets connector edits the cells directly | free |

To set them up you make **tokens** (like keys). Never paste a token into a chat. Put each one in the environment
settings under **Network secrets** (or as an environment variable) with these names, and a new session can use it:
- `META_PAGE_TOKEN` (or better `META_SYSTEM_USER_TOKEN`, which doesn't expire): Meta for Developers → create an app
  (free) → Business Settings → System users → generate a token for your Page and ad account with
  `pages_manage_posts`, `pages_read_engagement`, `ads_read` (and `ads_management` only if bots should prepare boosts).
- `META_AD_ACCOUNT_ID`, `META_PAGE_ID` (not secret, just numbers)
- `CLOUDFLARE_API_TOKEN`: Cloudflare → My Profile → API Tokens → template "Edit Cloudflare Workers"
- `YOUTUBE_API_KEY`: Google Cloud console → APIs → YouTube Data API v3 → Create key

Every posting, boosting or spending action still waits for your yes.

**Fix 2: jobs with no API keep a real browser.** These have no usable public API:
- Posting in **Facebook groups** (Meta closed the Groups API in 2024).
- **TikTok** public posting (TikTok only lets audited apps post publicly). The Higgsfield connector here has
  TikTok publishing tools: not tested, may cost credits.
- **Google Business Profile** pins and claims (API needs Google's approval).
- **WhatsApp from your own phone** (reminders: owner order 4 Nov says you send them yourself).
- The scanned **$100M Journal** in the Drive viewer.

For these, run a session **on your own computer**: the Claude desktop app, or `claude remote-control` in a
terminal in the folder to work in (it then shows up in the Claude Code app). There, Claude can use your Chrome
(Claude in Chrome works with Claude Code; not tested from here). Same repo, same bots. Or keep Cowork for just the
clicking jobs: the bots here write the exact text and steps, Cowork clicks.
Today no computer of yours is linked to this workspace (checked: none listed).

### C. Deploying the bot directly
The Cloudflare connector here can read but has no deploy tool, and `api.cloudflare.com` is blocked (A).
Until fixed: the bot writes the new file, you paste it into the Cloudflare editor (same as today).
After A + `CLOUDFLARE_API_TOKEN`: the bot deploys after your yes, keeping the old version for rollback.

### D. fal.ai downloads
`v3b.fal.media` is blocked (A). Until fixed, use the account skill `fal-media-to-sandbox`.

---

## "Free APIs from the internet": what's safe

- **Safe and free:** the official free tiers above (Meta, Google, YouTube, Cloudflare). You own the keys; nobody else sees your data.
- **Not safe:** lists of shared or leaked keys, "free GPT API" sites, cracked tools. They break the services' rules, can
  get your Meta or Google account banned (that would kill the Burhan 2 Page and the ads), and whoever runs them can
  read everything you send. Don't use them.
- **Cost of the team itself:** every chat (HeadBot and each bot) uses your Claude plan. Bots read books with cheaper
  worker agents and keep answers short (account skill `token-frugal`).

## Plugins that fail to connect

About 75 plugin connectors (HubSpot, Klaviyo, Ahrefs, Asana and others) fail here with "proxy 403". None of them is
part of your work today, so ignore them.
