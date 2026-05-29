# WeChat Publish Operating Model

Use this operating model unless you have already proved that the account supports formal publish APIs.

## Default Path

1. Preflight the article and credentials
2. Create a draft
3. Review in WeChat后台
4. Publish manually

This is the safest and most portable path.

## Why Draft-Only Is The Default

The automation may fail for reasons that are not content bugs:

- IP whitelist restrictions
- account-level interface permission differences
- image format issues
- network differences between runs

## What “Capability Proven” Means

Treat the account as capable of formal publish only after all of these have happened at least once:

- access token retrieval succeeded
- image upload succeeded
- draft creation succeeded
- `freepublish/submit` succeeded

Until then, keep the operating mode as `draft-only`.
