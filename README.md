# Ember HQ: your AI team in Claude Code

One **HeadBot** runs the team. Under it: **OfferBot**, **SalesBot**, **MarketingBot**.
They share one workspace (this repo), one live board (the Vanta Team Room) and one Drive folder.

```
                 Abdullahi
                     │
                  HeadBot ── brief, your orders, who does what, settles fights, second review
        ┌────────────┼────────────┐
    OfferBot     SalesBot     MarketingBot
  (what we sell) (leads → visits → buyers) (getting leads)
        └──── Vanta Team Room (orders · status cards · log · questions for John) ────┘
```

## Start in 4 steps

1. **Transfer.** Paste the prompt in `transfer/EXPORT-PROMPT.md` into your old Offer, Sales and Marketing chats
   (the same prompt in all three). Each one saves a file in Drive and sends you the link.
2. **File it.** Come back to HeadBot and type `/transfer`. HeadBot moves everything in and tells you what's missing.
3. **Open the team.** Type `/team`. HeadBot opens the three bot chats and gives you their links.
4. **Every day.** Start with HeadBot: `/brief`. Talk to a bot directly when you want a long session with it.

## Shortcuts

| Type | What happens |
|---|---|
| `/brief` | HeadBot's short brief: bottleneck, what needs your yes, fights, promises at risk |
| `/transfer` | Moves the old chats' exports into the workspace |
| `/team` | Opens the three bot chats |
| `/offerbot`, `/salesbot`, `/marketingbot` | Turns any new chat in this repo into that bot |

## What's better here than in the old chats

- HeadBot can **message the bot chats directly** and read what they did. You stop carrying questions between chats.
- Each bot's playbook is a **file with history**. Every change is saved and can be undone.
- Your skills still load here. HeadBot can also hand quick jobs to a helper bot without opening a chat.

## What doesn't work yet, and the fixes

Full list: `shared/capabilities.md`. The 3 fixes that unlock the most, all free:

1. **Open the internet for this workspace** (1 minute): environment settings → Network access → Full.
   Today Facebook, Google, YouTube, TikTok, WhatsApp and Cloudflare are blocked from here.
2. **Make a Meta token** (about 20 minutes): lets the bots read Ads Manager and Page numbers and post Reels to your Page
   through Meta's official API. They still ask you before posting or spending. Save it in the environment settings
   as `META_SYSTEM_USER_TOKEN`, never in a chat.
3. **Make a Cloudflare token** (5 minutes): lets SalesBot deploy a new bot version after your yes, instead of you pasting it.
   Save it as `CLOUDFLARE_API_TOKEN`.

Jobs that need **your** logged-in Chrome or phone (Facebook groups, TikTok Studio, Google Maps listing, WhatsApp from
your phone) need a session running on your own computer: the Claude desktop app, or `claude remote-control`.

## Where things are

| Folder | What's in it |
|---|---|
| `CLAUDE.md` | The rules every chat reads first |
| `bots/head/` | HeadBot: instructions, team list, work log |
| `bots/offer/`, `bots/sales/`, `bots/marketing/` | Each bot: `BOT.md` (who it is), `PLAYBOOK.md` (its method), `HANDOVER.md` (from the old chat) |
| `shared/` | Your standing rules, the Team Room guide, links and IDs, what works and what doesn't |
| `transfer/` | The prompt for the old chats |
| `edits/` | Video edit recipes |
