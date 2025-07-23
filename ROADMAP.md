# 🗺️ Sifely Cloud Integration – Roadmap

This document outlines planned features, improvements, and ideas for the future development of the Sifely Cloud integration.

---

## ✅ Completed (v1.0.0)
- Initial support for lock discovery via `/v3/key/list`
- Token authentication via `/smart/login`
- Lock command support (lock/unlock)
- Battery sensor
- Lock open/closed state sensor
- Lock history sensor with persistent CSV storage
- Coordinator-based architecture
- Diagnostic error sensor
- Configurable max number of locks and history entries
- UI-friendly history attributes and summary
- Privacy Lock and Tamper Alert binary sensors

## Next release
- GitHub Actions and version tagging
- README, license, and issue templates

---

## 🧭 Planned Features / Fixes

Maybe:
- [ ] For expired credentials, add async_step_reauth() support so the user can re-authenticate without removing the integration?
- [ ] Add a /diagnostics endpoint for easy bug reporting via the HA UI?
- [ ] Validate and sort lock history by timestamp (to guard against out-of-order entries)?
- [ ] Button to download the latest lock history to a .csv file via the www/ folder, or maybe email?
- [ ] Persist cloud error status.
- [ ] Update translations with any text out there.
- [ ] Look at UUID, token, or hashed identifier from web and find user name for history file.
- [ ] Lock schedule viewer/editor
- [ ] Doorbell / touch event detection (if supported)
- [ ] Configurable polling intervals
- [ ] Auto-restore lock history from cloud on reboot

Thinking about:
- [ ] Rename locks from Home Assistant UI.
- [ ] Show lock timezone settings.
- [ ] Lock configuration sync (from app → HA). ( Confirm)
- [ ] Optional persistent notification on tamper alert.
- [ ] Push notification integration (via HA Notify service).
- [ ] Chart view of lock usage over time.
- [ ] History trend analysis in UI (via custom panel or HACS card).
- [ ] Option to disable polling (manual update only? )
- [ ] Better handling for gateway busy/timeout edge cases.
- [ ] QR Code-based setup via UI (This would be cool)


---

## 💬 Suggestions?

I welcome feedback and feature requests!
Please [open an issue](https://github.com/kenster1965/sifely_cloud/issues/new/choose) if you have an idea you'd like to see included.
