# Model Spec: Stylized Bank Interest Rate Risk (v1)

## Purpose
Measure how a simplified Canadian bank's net interest income (NII, 12 months) and economic value of equity (EVE) respond to interest rate shocks, using Government of Canada yields from the Bank of Canada. v1 is an Excel prototype (`model/bank_balance_sheet.xlsx`). v2 rebuilds it in Python with the full yield curve.

## Scope
Banking book only: loans, securities, cash, deposits, and funding. Excludes trading assets, derivatives, and reverse repos. The balance sheet is modeled on RBC's 2025 annual report (Table 36, Oct 31, 2025). Loans, securities, and cash ($1,691.6B) are rescaled to $100B. Against that base, deposits are about 90% and equity about 8%.

## Balance sheet (in $B)
| Line | Balance | Rate (%) | Reprices in 12m (%) | Duration (yrs) | Deposit beta |
|---|---|---|---|---|---|
| Fixed-rate 5-yr mortgages | 39 | 4.38 | 20 | 3 | n/a |
| Floating-rate commercial loans | 23 | 4.86 | 100 | 0.25 | n/a |
| Government bonds (7-yr) and cash | 38 | 3.67 | 20 | 5 | n/a |
| Chequing and savings deposits | 55 | 0.80 | 100 | 2.5 | 0.30 |
| Term deposits and GICs (1 to 5 yrs) | 35 | 3.06 | 33 | 1.5 | 1.0 |
| Wholesale and other funding | 2 | 3.61 | 100 | 0.25 | 1.0 |
| Equity | 8 | n/a | n/a | n/a | n/a |

## Data
Yields from the Bank of Canada Valet API (2, 3, 5, 7, 10-year and long-term benchmark bonds), daily from 2015-01-01 to 2026-10-29, saved in `data/yields.csv`. Yields used in v1 (Oct 29, 2026): 5-year 3.58, 7-year 3.67, short rate 3.36 (the 2-year yield as a stand-in for the policy rate).

## Method
- NII = sum of (balance x rate) on assets minus the same on liabilities. NIM = NII / total assets.
- Change in NII over 12 months = [sum of (asset balance x share repricing) minus sum of (liability balance x share repricing x deposit beta)] x rate shock.
- Change in EVE, approximately = minus [sum of (asset balance x duration) minus sum of (liability balance x duration)] x rate shock.

## Assumptions
Data: the yields above. Everything else is an assumption.
- Spreads: mortgages 0.80 over the 5-year yield, commercial loans 1.50 over the short rate, wholesale funding 0.25 over the short rate, GICs 0.30 below it. They cover credit risk, funding, costs, and margin.
- Chequing and savings pay 0.80. The split of deposits between chequing and savings (55) and GICs (35) is assumed, since Table 36 doesn't break it down.
- Repricing: a 5-year mortgage book spread evenly resets about a fifth each year, bonds about a fifth (a ladder plus some cash), and a 1 to 5 year GIC ladder about a third.
- Durations are rough approximations. Mortgages are below 5 because principal is repaid. Chequing and savings use an assumed behavioural duration of 2.5.
- Deposit betas: 0.30 for chequing and savings, 1.0 for GICs and wholesale funding.
- The assumptions were chosen so that the signs match RBC's disclosure. That is calibration, not a result.

## Results (+100 bps parallel shock)
- NII is 2.64 on $100B of assets, a NIM of 2.64% (RBC's reported NIM: [fill in]).
- Change in NII: +0.084 ($84M per $100B).
- Change in EVE: -1.22 ($B), or -15.3% of equity.

## Validation against RBC (Table 49, Oct 31, 2025)
- +100 bps: NII +$197M, EVE -$2,648M (-1.9% of equity of $139,151M).
- -100 bps: NII -$373M, EVE +$1,932M.
- The signs match in both directions. The size of the EVE move does not: my model's is about 8 times larger as a share of equity.
- Hypotheses to check in RBC's market risk discussion: RBC hedges its interest rate risk, which keeps its duration gap near 0.1 years against about 1.2 here, and real balance sheets have options and behavioural effects that make results asymmetric. My model is linear, so +100 and -100 come out symmetric.

## Scenarios to run in v2
Parallel +/-100 and +/-200 bps, a steepener, and a flattener, calibrated to observed moves: the 2022 to 2023 flattening and inversion (703 inverted days since 2015, 248 of them in 2023) and the recovery since.

## Limitations
- Parallel shocks only in v1, since steepeners and flatteners need the full curve.
- Static balance sheet with no growth or prepayments, and NII measured over 12 months.
- Duration is a linear approximation.
- Unhedged, with no options.
- Assumed betas, durations, spreads, and deposit split.
- The model covers one stylized bank and is not a forecast for RBC.

## Out of scope
Trading book, foreign exchange, credit risk, basis risk, prepayment modelling, and behavioural modelling beyond deposit betas.

## Test for v2
With the same inputs, the Python model must reproduce a +100 bps change in NII of +0.0835 and change in EVE of -1.2225.