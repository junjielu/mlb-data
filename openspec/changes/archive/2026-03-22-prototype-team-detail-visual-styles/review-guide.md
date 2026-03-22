# Team Detail Visual Refresh Review Guide

## Access

- Start the local frontend server from the repo root with `python3 scripts/serve_web.py --port 4174`.
- Open any team detail page such as `http://127.0.0.1:4174/team/NYY`.
- The page has been converged to the selected `Editorial` direction, so no prototype switcher is shown in the UI.

## Review Checklist

- Confirm Batter, SP, RP, and Current Injury Report still appear in the same order.
- Confirm table sorting and expandable history rows behave the same after the visual refresh.
- Confirm player links still open Fangraphs in a new tab.
- Confirm the injury section still distinguishes between empty-team rows and unavailable injury data.
- Confirm the simplified hero, Batter readability improvements, and SP role badges feel production-ready on desktop and narrow screens.

## Convergence Notes

- Selected direction: `Editorial`.
- Prototype switcher UI, alternate visual variants, and review-only comparison copy have been removed from the implementation.
- If the final visual refresh should extend to `/teams`, capture that as a follow-up change rather than broadening this prototype change during review.
