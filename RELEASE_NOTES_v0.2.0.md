# v0.2.0

`reading-wechat-publisher` enters its second iteration with a tighter writing workflow, stronger visual defaults, and a verified WeChat formal publish path.

## What This Release Covers

- keep source honesty and writing mode choices explicit through the reading workflow
- make Guizang-style covers and knowledge cards the default visual route
- improve WeChat article packaging so longform output reads cleaner on mobile
- preserve a `draft-first` publishing model while supporting formal publish once account conditions are proven
- document the companion daily `06:30` reading-and-publish automation pattern used in the active workspace

## Key Workflow Changes

- `guizang-social-card-skill` is now the default route for knowledge cards
- WeChat articles no longer default to repeating the article title inside the body
- `reading-social-publisher` is positioned more clearly as the cross-channel orchestration layer

## Verified In Practice

- live WeChat formal publish succeeded after validating `AppID`, `AppSecret`, and IP whitelist settings
- the updated workflow was exercised on a full book-note to published-article run
- the companion workspace automation now supports a queued booklist with path registration and publish tracking

## Practical Boundaries

- WeChat is still safest as `draft-first` unless the account is known to support formal publish cleanly
- Xiaohongshu still needs one manual image-upload step before browser automation can continue
- the daily automation controller lives in the active workspace companion directory, not inside this plugin repository

## Repository

GitHub: [woohuaca/reading-wechat-publisher](https://github.com/woohuaca/reading-wechat-publisher)
