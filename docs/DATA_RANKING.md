# Data Ranking and Expansion Priorities

Source: `artifacts/data_coverage_report.json`

SECTION A — Top 20 Largest Datasets

Columns: market | timeframe | rows

1. BTCUSDT | 1h | 56201
2. BTCUSDT | 4h | 14058
3. EURUSD  | 1h | 12300
4. XAUUSD  | 1h | 11417
5. USOIL   | 1h | 11200
6. US30    | 1h | 3469
7. EURUSD  | 4h | 3169
8. XAUUSD  | 4h | 3094
9. USOIL   | 4h | 3057
10. BTCUSDT| 1d | 2344
11. EURUSD | 1d | 1668
12. USOIL  | 1d | 1612
13. XAUUSD | 1d | 1612
14. US30   | 1d | 1610
15. US30   | 4h | 1161

SECTION B — Top 20 Smallest Datasets

Columns: market | timeframe | rows

1. US30   | 4h | 1161
2. US30   | 1d | 1610
3. USOIL  | 1d | 1612
4. XAUUSD | 1d | 1612
5. EURUSD | 1d | 1668
6. BTCUSDT| 1d | 2344
7. USOIL  | 4h | 3057
8. XAUUSD | 4h | 3094
9. EURUSD | 4h | 3169
10. US30  | 1h | 3469
11. USOIL | 1h | 11200
12. XAUUSD| 1h | 11417
13. EURUSD| 1h | 12300
14. BTCUSDT|4h | 14058
15. BTCUSDT|1h | 56201

SECTION C — Market Coverage Matrix

Columns: 1m | 5m | 15m | 30m | 1h | 4h | 1d

- BTCUSDT: NO | NO | NO | NO | YES | YES | YES
- EURUSD:  NO | NO | NO | NO | YES | YES | YES
- XAUUSD:  NO | NO | NO | NO | YES | YES | YES
- USOIL:   NO | NO | NO | NO | YES | YES | YES
- US30:    NO | NO | NO | NO | YES | YES | YES

SECTION D — Missing Timeframes

- BTCUSDT: [1m, 5m, 15m, 30m]
- EURUSD:  [1m, 5m, 15m, 30m]
- XAUUSD:  [1m, 5m, 15m, 30m]
- USOIL:   [1m, 5m, 15m, 30m]
- US30:    [1m, 5m, 15m, 30m]

SECTION E — Expansion Priority

Priority 1 — Existing markets missing intraday timeframes (high priority):
- BTCUSDT, EURUSD, XAUUSD, USOIL, US30 (add 1m, 5m, 15m, 30m where feasible)

Priority 2 — Markets with very low data volume (medium priority):
- US30 (largest timeframe rows ~3.5k) — add more history or intraday feeds to increase sample size

Priority 3 — Completely missing markets (lower priority; new markets require procurement):
- GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAGUSD, NAS100, SPX500, GER40, UK100, UKOIL, NGAS, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT

Files:
- artifacts/data_ranking.json (JSON representation of these tables)
