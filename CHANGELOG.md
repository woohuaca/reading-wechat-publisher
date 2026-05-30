# Changelog

## v0.2.0 - 2026-05-30

Second iteration of `reading-wechat-publisher`, shaped by live publishing runs and workflow hardening.

### Changed

- Guizang-style visual packaging is now the default path for knowledge cards and stronger cover work
- WeChat article packaging now defaults to avoiding a repeated title as the first body heading
- WeChat publishing guidance is now explicit about a `draft-first` operating model with optional formal publish after credentials, permissions, and IP whitelist are validated

### Added

- release guidance for more stable cross-channel orchestration through `reading-social-publisher`
- clearer documentation around source modes and writing modes carried through the reading workflow
- companion iteration notes for the validated daily `06:30` reading-and-publish automation pattern used in the active workspace

### Verified

- WeChat formal publish has now been proven in a live run when valid `AppID`, `AppSecret`, and IP whitelist settings are present
- the updated Guizang-first workflow was exercised on a full book-note to published-article cycle

### Notes

- WeChat remains safest as `draft-first`, even though formal publish is now a validated option when account conditions are satisfied
- Xiaohongshu still requires a manual image-upload step in the browser before the automation can continue

## v0.1.0 - 2026-05-30

Initial published version of `reading-wechat-publisher`.

### Included

- `reading-strategy` for structured book-note generation
- `wechat-article-designer` for mobile-first WeChat article packaging
- `wechat-publisher` for preview, preflight, and WeChat draft creation
- `reading-social-publisher` as the top-level orchestration skill
- bundled Python scripts for preview, validation, and WeChat draft publishing
- Guizang-oriented integration guidance for stronger covers and knowledge cards
- Xiaohongshu / Rednote draft workflow notes with browser-assisted handoff

### Notes

- WeChat defaults to `draft-only`
- Xiaohongshu currently requires a manual image-upload step before browser automation continues
