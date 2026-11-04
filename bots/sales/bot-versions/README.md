# Bot versions

One file per version of the Vanta bot (`ember-agent` worker) plus the patch script that made it, e.g.
`worker_v1_14_5.js` and `patch_v1145.py`. Keep the live version's file for rollback.
Live on 4 Nov 2026: v1.14.4 (Sales' card, checked by Sales at 1:18 AM). Its file is not in this repo yet:
get it with the Cloudflare connector (`workers_get_worker_code`, worker `ember-agent`).
