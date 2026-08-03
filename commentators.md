# Commentators

22 commentators, in `commentator.sort_order` (display order, matches source JSON key order).
"verses with Sanskrit" = count of verses where that commentator has an `sa` commentary row
(out of 719 total verses); not all commentators have a Sanskrit source text.

| ord | id | author | verses with Sanskrit |
|---|---|---|---|
| 0 | tej | Swami Tejomayananda | 1 |
| 1 | siva | Swami Sivananda | 1 |
| 2 | purohit | Shri Purohit Swami | 1 |
| 3 | chinmay | Swami Chinmayananda | 1 |
| 4 | san | Dr.S.Sankaranarayan | 1 |
| 5 | adi | Swami Adidevananda | 1 |
| 6 | gambir | Swami Gambirananda | 1 |
| 7 | madhav | Sri Madhavacharya | 717 |
| 8 | anand | Sri Anandgiri | 717 |
| 9 | rams | Swami Ramsukhdas | 1 |
| 10 | raman | Sri Ramanuja | 717 |
| 11 | abhinav | Sri Abhinav Gupta | 716 |
| 12 | sankar | Sri Shankaracharya | 717 |
| 13 | jaya | Sri Jayatritha | 717 |
| 14 | vallabh | Sri Vallabhacharya | 717 |
| 15 | ms | Sri Madhusudan Saraswati | 717 |
| 16 | srid | Sri Sridhara Swami | 717 |
| 17 | dhan | Sri Dhanpati | 717 |
| 18 | venkat | Vedantadeshikacharya Venkatanatha | 717 |
| 19 | puru | Sri Purushottamji | 717 |
| 20 | neel | Sri Neelkanth | 717 |
| 21 | prabhu | A.C. Bhaktivedanta Swami Prabhupada | 0 |

Every commentator has all 4 target languages (hi/en/be/ka) on all 719 verses. The Sanskrit
count above is only about the optional Sanskrit source text (`sa`).

## Data quirks (upstream in source JSON, not introduced by conversion)

- The 8 commentators normally sourced from Hindi/English (tej, siva, purohit, chinmay, san,
  adi, gambir, rams) each have exactly one `sa` row, all on verse **BG9.35**, all ~70
  characters — likely a colophon line that leaked into those blocks, not real Sanskrit
  commentary.
- **BG6.48** and **BG7.31** lack Sanskrit for madhav/raman/abhinav (717 instead of 719) — the
  same two files that were also missing the `author` key entirely (see PLAN.md). Both verses
  are generally degraded upstream.
- **BG6.19** additionally lacks abhinav's Sanskrit (abhinav is 716, one lower than the other
  717s).
