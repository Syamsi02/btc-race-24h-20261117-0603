# btc-race-24h-20261117-0603

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/Syamsi02/btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/Syamsi02/btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A bot for the make.fun "Race a BTC trading bot live for 24 hours" bounty
(`btc-race-24h-20261117-0603`). It trades one asset, Coinbase Wrapped BTC
(CBBTC) against USDC, on 1-minute bars, starting from $1,000 of paper money.
Long only, one open position at a time, all-in sizing.

## Run it

```sh
python3 main.py
```

## How it works

The bot keeps the history of closes and two integer exponential moving
averages (a fast 5-bar one and a slow 240-bar one, both scaled by 1,000,000
and seeded at the first close, so every calculation is exact integer math
and the bot is fully deterministic).

**Entry** — only while flat, and only once at least 60 bars of history exist.
It looks back at the previous 120 closes and measures how far the current
close has fallen from their high:

- the dip must be at least 120 bps below that high;
- the price must be bouncing: the close is above the previous close and
  above the fast EMA;
- and either the close is above the slow EMA (the longer trend is up) or
  the dip is deep, at least 300 bps.

When all three hold it buys with all of its cash.

**Exit** — while holding, it sells everything on the first of:

- take profit: the close is 100 bps above the average entry price;
- stop loss: the close is 200 bps below the average entry price;
- time exit: 480 bars (8 hours) have passed since the batch on which the
  buy was decided.

Every order allows 100 bps of slippage from the latest close. Anything
still held when the window ends is flattened by the harness.

## Files

- `main.py` — the bot (Python 3.13, standard library only). It puts its own
  directory on `sys.path` before importing the vendored shim, because the
  trials launch it with `python3 -P -s main.py`.
- `vendor/makefun_bars.py` — byte-for-byte copy of the kit's Python shim for
  the `agent-fun/bars-replay/v1` protocol; it owns the wire (one reply per
  batch, echoing the batch seq) and keeps the account state.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=fgwhnby2&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
