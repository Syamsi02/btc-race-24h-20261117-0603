"""Dip-and-recover CBBTC bot for the make.fun BTC race.

The harness speaks agent-fun/bars-replay/v1: it sends one hello line, then
one batch per bar (each batch carries the bar that just closed, the fills of
the previous batch's orders, and the account), then done. This bot answers
every batch with exactly one reply echoing its seq, carrying its orders.

Idea: sit in cash, wait for price to dip a clear distance below its recent
high and tick back up while the short trend turns up, then buy with all cash
and hold for a small gain, a wider stop, or a time limit. All arithmetic is
integer only, so two runs on the same bars give the same orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
SCALE = 1000000
DIP_ENTRY_BPS = 120
DIP_STRONG_BPS = 300
TAKE_PROFIT_BPS = 100
STOP_LOSS_BPS = 200
HOLD_BARS = 480
WARMUP_BARS = 60
LOOKBACK = 120

closes = []
ema5 = 0
ema240 = 0
entry_seq = None


def _ema_update(prev, close, n):
    return (close * SCALE * 2 + prev * (n - 1)) // (n + 1)


def on_batch(state, batch):
    global ema5, ema240, entry_seq
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return []
    close = int(bar["c"])
    prev_close = closes[-1] if closes else close
    closes.append(close)
    if len(closes) == 1:
        ema5 = close * SCALE
        ema240 = close * SCALE
    else:
        ema5 = _ema_update(ema5, close, 5)
        ema240 = _ema_update(ema240, close, 240)
    pos = state.positions.get(SYMBOL)
    qty = pos.qty if pos is not None else 0
    if qty <= 0:
        entry_seq = None
        if state.warming_up or len(closes) <= WARMUP_BARS:
            return []
        window = closes[:-1][-LOOKBACK:]
        high120 = max(window)
        dip_bps = (high120 - close) * 10000 // high120
        bounce = close > prev_close and close * SCALE > ema5
        trend_up = close * SCALE > ema240
        if dip_bps >= DIP_ENTRY_BPS and bounce and (trend_up or dip_bps >= DIP_STRONG_BPS):
            entry_seq = state.seq
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": 100}]
        return []

    entry_price = pos.cost * 10 ** 13 // (qty * 10 ** 6)
    take_profit = close * 10000 >= entry_price * (10000 + TAKE_PROFIT_BPS)
    stop_loss = close * 10000 <= entry_price * (10000 - STOP_LOSS_BPS)
    timed_out = entry_seq is not None and state.seq - entry_seq >= HOLD_BARS
    if take_profit or stop_loss or timed_out:
        return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                 "max_slippage_bps": 100}]
    return []


makefun_bars.run(on_batch)
