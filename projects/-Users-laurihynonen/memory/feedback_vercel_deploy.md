---
name: Deploy via GitHub, not Vercel CLI
description: For slide-sage (and likely other Vercel projects), deploy by pushing to GitHub — Vercel auto-deploys from Git
type: feedback
---

Always deploy by committing and pushing to GitHub instead of running `vercel --prod` directly.

**Why:** Vercel is connected to GitHub and auto-deploys on push. This keeps GitHub and Vercel in sync. Deploying via CLI bypasses Git and leaves GitHub out of date.

**How to apply:** When the user asks to deploy a Vercel project, commit the changes and push to GitHub instead of running `vercel --prod`.
