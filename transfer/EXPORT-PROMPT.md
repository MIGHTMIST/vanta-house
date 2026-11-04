# Transfer prompt: paste this into each old chat

**How to use it (Abdullahi):**
1. Open your **Offer** chat in claude.ai. Copy everything between the two lines below and send it.
2. Do the same in the **Sales** chat and the **Marketing** chat. It's the same prompt for all three; each chat knows who it is.
3. Each chat saves ONE file in Drive, in "Vanta Team Room - All Papers", and sends you the link.
4. Come back to HeadBot (Claude Code) and type `/transfer`. HeadBot reads the three files and moves everything in.

If a chat says it ran out of room, reply "continue" until it says DONE.

---

```text
We are moving the team to a new home: Claude Code. There will be one HeadBot that runs the team, and under it
OfferBot, SalesBot and MarketingBot, each in its own chat, sharing one workspace. You are one of my department
chats (Offer, Sales or Marketing). I need you to hand over EVERYTHING you know, so the new bot can carry on exactly
where you stop, without asking me again.

Make ONE file in my Google Drive folder "Vanta Team Room - All Papers"
(folder id 1icSdj9jbIJwPcGphUqvnS54rN06-2qeP). Name it: "TRANSFER - <your department> - <today's date and time>".
Use plain text or Markdown. Complete beats short: do NOT summarise, do NOT write "see above" or "PLACEHOLDER".

Put these sections in it, in this order, with these exact headings:

## 1. WHO I AM
Your department, your one job in one line, and what you call yourself.

## 2. PLAYBOOK
The newest FULL text of your department skill (your SKILL.md), word for word, from the first line to the last.
Add everything you learned that is not in the saved skill yet (new rules, owner processes, book notes, lessons),
in the right place, and mark each added part with "(new, not yet saved)". If you made a skill update that is
waiting for my approval, put that version here and say so.

## 3. NEW SKILLS
Any other repeatable process you do that has no skill yet. Write each one as a complete SKILL.md
(name, one-line description of when to use it, then the steps). Write "none" if there are none.

## 4. PROJECT INSTRUCTIONS AND FILES
If this chat is inside a Project: copy the project instructions word for word. List every project knowledge file:
name, what it is, and where a copy lives (Drive link). If a file exists only in the project, upload it to the
folder above first and give the link.

## 5. MEMORY
Everything you remember about me, my business, my clients (Vanta House / John, Burhan 2, Praxis, others), the
people, my preferences and the way I like to work. Include anything from your memory or earlier chats.

## 6. CURRENT WORK
What you were doing when I sent this. The next 3 steps, in order. What you are waiting for, and from whom.

## 7. DECISIONS
Every decision, dated (date and time), who made it (me, you, another department), and whether it is still
active or was replaced (and by what).

## 8. OPEN QUESTIONS AND DISAGREEMENTS
Questions waiting for me, for John, or for another department. Every disagreement with another department or
with me: both sides, the evidence, and your recommendation.

## 9. NUMBERS
Every number you rely on (prices, funnel, ad results, costs, dates), each with its source and a label:
checked / estimate / my pick / not checked.

## 10. FILES AND LINKS
Every file, page, PDF, artifact, sheet, video and bot version you made or use: name, what it is, link.
If something exists only inside this chat or on a local computer, upload it to the folder above first,
then give the Drive link. Say which ones you could not upload.

## 11. TOOLS AND HOW I USED THEM
Every tool, connector, website and account you used (for example Chrome / Meta Business Suite / Ads Manager,
Cloudflare, Drive, Canva, fal, Higgsfield, WhatsApp). For each: what for, the IDs or names you need, and the exact
steps. Mark the jobs that needed my Chrome, my screen or my phone. Do NOT write passwords, tokens or keys:
say where they are stored instead.

## 12. MISTAKES AND LESSONS
What went wrong, why, and the rule that stops it happening again.

## 13. PROMISES
Every promise made to a buyer, to John, to a client or to me: who promised, what, by when, and whether it is kept.

## 14. FIRST HOUR IN THE NEW HOME
What the new bot should do first, in order, and what it must NOT do.

When the file is saved, reply with: the file link, a 5-line summary, and a list of anything you could not save
or are not sure about. If you cannot write to Drive, paste the whole thing here instead, in parts labelled
"PART 1 of N", and end with DONE.
```

---

**Why a Drive file and not a paste:** the exports will be long (the Marketing skill alone is about 46,000 characters).
A Drive file can't get cut off, and HeadBot can read it directly from here (checked: Drive works in this workspace).
