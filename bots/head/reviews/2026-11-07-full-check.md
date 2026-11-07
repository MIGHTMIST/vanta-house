# Full check, 7 Nov 2026 — "How is the plan? Good or bad?"

Asked by Abdullahi: look through everything in the shared Drive, one by one, with his methods, Sonnet helpers, HeadBot as the brain.
Method: 6 items in order (one finished before the next). Each item read by a Sonnet helper; HeadBot then checked the key
findings against the source itself (raw WhatsApp chat, permits, the papers' own text, the live bot code). Methods used:
constraint order, bullshit meter (GREEN/AMBER/RED), Logic/Evidence/Utility, no guessing (labels, maths in python),
flaws first, prepare-to-win pre-mortem + one-way doors, math-or-test, liability lens, 13-point proof checklist.
Read-only: nothing was changed in Drive, the Team Room or the bot.

## Verdict
**Direction: good. The plan as written: not ready (mixed, leaning bad). Trust about 40/100. Risk if acted on as is: high.**
The plan aims at the right constraint (the first real site visit) with the right shape (one goal, one CTA, fix the bot
before posting, no price without a dated list). But the bot — the "counter" in the plan's own flyer story — is broken
today, the money line exists in three versions, and most promises rest on John's spoken word, not his written word.

## Item 1 — Ground truth (John's own words). MIXED, 60/100.
- Number on John's videos: John wrote 29 Oct "the main video must display only our names, job titles, and phone numbers"
  and called not following it "pointless". The yes to the bot number is in person only. RED until written.
- Money: UGX 1M for 5 videos paid (GREEN, chat). UGX 3.3M = Abdullahi's own message, no reply; "3 million" = in person.
  Commission: "Any commission from the clients you bring in will be yours" — no %, tied to own-number videos. RED (unwritten).
- John's terms (3 Nov): "Higher down payments qualify for lower prices and greater discounts" — no amount.
- Two plans in one message batch: "30% + 20 months" vs "20%–50% + 12–15 months". No interest mentioned.
- Prices 53,800 / 95,000 / 166,000 identical on 26 Oct, 27 Oct, 3 Nov; list undated; "3% every two months from 31 Aug".
- "Fully finished": not in the chat (Abdullahi's 26 Oct opener); may be on Blackstone's website / purchase guide (unchecked).
- Permits: Plot 3 GREEN. Development permit: 13 levels, no building before a building permit; building permit dated
  2 Oct 2026; John: 7th floor on 3 Nov at 2.5 floors/month. Dates don't line up — a question, never an accusation.
- John's own selling points use banned claims (15% yield, 7-year payback, China Speed, low investment).

## Item 2 — VANTA ONE PLAN draft 4. MIXED leaning BAD, 38/100.
- Not agreed: no AGREE from Sales or Offer on draft 4; "Differences left: None" while asking both to change.
- No finish line: "the first real buyer at the site" has no date, number or stop rule.
- Bot check "can pay 50% first" + 5 Nov silent-treatment order = a 30% buyer is closed and ignored. Biggest money leak.
- Reward box: furniture pack (nobody priced it, "Who: Abdullahi"), live video call abroad (cites 2 Nov; reversed 4 Nov
  1:18 AM), pick-up (Abdullahi's cost, no cap) — none from John.
- Solid: one goal, one CTA, bot before flyers, dated price list rule, urgent-only John questions, honest "not tested" on Meta.

## Item 3 — The offer and the public line. MIXED leaning BAD, 45/100.
- The 11:34 PM 6 Nov order is not in the orders box; three retellings give three public lines (Offer: "A finished flat ...
  Pay 50% first for the best price, or start from 30%"; Marketing: "Pay 50% first, then equal monthly payments";
  Sales: "... your first year's management fee is free and you pick your flat before others").
- Offer page: "BEST PRICE ... lower price and a bigger discount", "The 50% discount figure: John gives it at the table",
  "Rent return about 15% a year, back in about 7 years", "A finished flat". Price cut with no amount, banned claims,
  "finished" reads as ready now.
- 50% vs 30% as the public line = a TEST question (total price is the same; 50% only moves John's cash earlier).
- Weakest Value Equation lever: perceived likelihood (0 visits, 0 sales). Rewards don't move it; a first real visit does.

## Item 4 — Today's John questions paper. MIXED, 55/100.
- Header says "Everything else you already told us" / "其他问题您都已经回答了" — false (about 15 items unanswered).
- Drops 3 of the owner's keep-list (amenities in the agreement, buyer money account, papers and when); no "date of the
  price list"; no tick box for the bot number. 1 Nov list got only "OK Please".
- Corrected 8 questions + corrected Chinese: scratchpad check7/4-john-questions/NOTES.md (given to Abdullahi in chat).

## Item 5 — Sunday filming. MIXED, 50/100.
- Offer's walking order uses v8 step numbers; v8.1 papers are renumbered (step 21 = a hook on one, John's helmet on the other).
- Director notes inside John's spoken lines: "(say it only if it is true)", "(say it only if you agree)", "(say it only
  if the payment plan is given in writing)".
- No written yes from John for Sunday. CTA has no number (good: make the number an edit graphic, reversible).
- Fixed in v8.1: ten years, "we'll book your time", no 6/3/1, lift cut, parking "planned", papers = stamps only.
- Day: ~7 hours of John on camera with no break; helmets for both from the gate; no backwards walk; 1080p HEVC, 30 GB
  free, a mic; edit 3 videos for Monday, queue the rest.

## Item 6 — Bot + Meta signals. BAD for Monday as things stand, 25/100.
- Live bot = v1.14.4, last changed 3 Nov 21:43 UTC (Cloudflare). VANTA_WORDS = VANTA, PLAN, PAY, SITE, VIEW, HOME, NAGURU,
  TOUR — no VISIT. A new lead sending VISIT gets Ember's pitch ("Ember doesn't sell plots or rent houses").
- Live bot still says "20% to 50%", "fully finished", offers a live video walk.
- Number: ember-agent's Vanta comment says reels use "+256 776 756 124"; praxis-bot (Apple Residency demo v1.4.2) has
  BOT_NUMBER default "256741131420". So 0741 131 420 may point at the demo bot. Check in WhatsApp Manager before Monday.
- Meta events: three different event maps (guide / live code / Sales log); "QualifiedLead" not found in Meta sources the
  helper could reach — likely refused. Don't block launch on it.
- Facebook/Messenger blocked in Uganda since the Jan 2026 election (OONI, Internet Society, via search; current status
  unverified): WhatsApp CTA is right.

## Root causes
1. Owner orders given in chats but not written in the orders box (11:34, 11:37, 11:38 PM 6 Nov) → three retellings.
2. Three departments make the same paper in parallel (three routes, three public lines, three event maps).
3. John's spoken yes treated as agreed; nothing in writing (number, money, commission, rewards, Sunday).
4. "Use only what we have; if it clashes later, fix it then" replaced "any line John does not confirm is cut".

## Fix order (one at a time)
1. Abdullahi types the ONE public line into the orders box. HeadBot pick: "Pay 50% first, then equal monthly payments.
   Or start from 30%." No "best price", "discount", "finished", "first year free", "pick first" until John writes them.
2. Today with John: written WhatsApp yes on the bot number, Sunday + 7:30 AM, stamps on camera, the rewards; ask the
   discount size; privately, commission and the 3M.
3. Bot: verify where 0741 131 420 points; paste + test v1.15 Saturday night from a second phone (VISIT, "visit", "Hi VISIT");
   money check passes at 20%+, 50% only picks the reward; silence only for clear no-fits; no posting until VISIT works
   (plan B: Abdullahi answers by hand).
4. Sunday: print only v8.1 (both papers); cut the notes from John's lines; helmets for both; food break; edit 3 for Monday.
5. The plan gets a finish line: e.g. "first real visit by [date]; if 0 visits after N bookings, stop and rethink"
   (estimate from the first campaign: ~USD 31 per booking → 2–4 bookings ≈ USD 62–124 for a first visit at 50–25% show-up).
