# Unilateral Pairs Trading System

> **Source:** Abstracted from *Trade Like a Hedge Fund* by James Altucher (2004).

## Notation

| Symbol | Meaning |
|---|---|
| **P1** | The most volatile pair (e.g. QQQ) |
| **P2** | The most stable pair (e.g. SPY) |

**Core idea:** for each day, calculate the difference between the ratio (P1 / P2) and its moving average. When P1 diverges sharply from its usual relationship to P2, trade P1 as the "culprit" and expect the spread to revert.

---

## The Unilateral Pairs Trading System — QQQ (P1) / SPY (P2)

1. Calculate the **ratio** of the P1 price series over the P2 price series.
2. Calculate the **20-day moving average** of that ratio.
3. For each day, calculate the **difference** between the ratio and its moving average.
4. Calculate the **20-day moving average** of those differences.
5. For each day, calculate how many **standard deviations** that day's difference is from the moving average. Compute the standard deviation for each day using its prior 20 days.
6. **Short entry:** for each day, if the standard deviation calculated is **greater than 1.5** *and* P1 is **2% greater** than the prior day, then **short P1**. (The spread between P1 and P2 has become much greater than usual; if P1 also had a big up move, P1 is most likely the culprit and needs to be shorted.)
7. **Long entry:** for each day, if the standard deviation calculated is **less than −1.5** *and* P1 is **2% lower** than the prior day, then **buy P1 (QQQ)**.
8. **Exit:** sell/cover when the standard deviation of the difference in the ratio is **less than 0.5** (in the case of a short) or **greater than −0.5** (in the case of a long).

This is the system for unilateral pairs trading and will be represented as Python code.
