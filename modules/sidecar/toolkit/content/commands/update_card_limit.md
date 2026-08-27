---
name: update_card_limit
description: Update credit card limit in ratchet progress tracker
argument-hint: card-name new-limit [date]
agent: agent
---

Collect all values from the user in chat — do NOT run any terminal commands until all values are confirmed.

Step 1 — Ask for card name:
- Show this static list and ask the user to pick one:
  1. Costco Anywhere → `costco_anywhere`
  2. MGM Rewards → `mgm_rewards`
  3. Venture → `venture`
  4. Apple Card → `apple_card`
  5. Best Buy → `best_buy`
  6. Buckle → `buckle`
  7. Home Depot → `home_depot`
  8. PayPal Credit → `paypal_credit`
- Accept aliases: "Venture", "Capital One Venture", "Capital One", "CapOne" → `venture`

Step 2 — Ask for new limit (integer, no commas needed).

Step 3 — Ask for date. Default: today (2026-04-06). Accept YYYY-MM-DD or MM/DD/YYYY.

Step 4 — Run the script to get current limit data and write the update:

`uv run --no-sync python -m modules.financials.update_card_limit --card="$CARD" --limit=$LIMIT --date="$DATE" --yes`

The script output shows the full update summary and progress table — display it to the user.
