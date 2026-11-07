---
name: personal-finance
description: >
  Personal money management for Eng. Hamed Al-Harmali (Omani entrepreneur, owner of IHP Oman,
  TLE and Shawarma Qasyoon), in OMR. Covers household budgeting, personal cash flow, savings
  and emergency fund, debt and loan payoff, net worth tracking, financial goals (Hajj, property,
  education, retirement, children), and above all the line between personal money and business
  money. Use this skill whenever the user mentions personal budget, my spending, my salary or
  owner draw, how much should I save, emergency fund, personal loan or mortgage, car loan,
  net worth, am I on track, retirement, family expenses, "my money", paying myself from the
  company, mixing personal and business accounts, or asks to review a bank statement or
  personal expenses, even if they never say "personal finance". Business cash flow, quotations
  and ROI of company projects belong to finance-cash-tracker and investment-feasibility-roi,
  not here.
---

# Personal Finance (Chief of Staff for the owner's own money)

## Why this exists
For a multi-business owner, personal finance is mostly a boundary problem. Money drifts
between IHP Oman, TLE, the café and the household, and nobody notices until cash is tight
or an auditor asks. Fix the boundary first; budgeting tips come second.

## Standing context
- Currency: OMR. 1 OMR = 1,000 baisa; always show 3 decimals (e.g. OMR 1,250.500).
- Owner of IHP Oman, TLE and Shawarma Qasyoon. Income is lumpy (project payments, café
  takings, principal commissions), so budget off a conservative baseline, not the best month.
- Personal development spend (ERMA CPD, PMP) is a legitimate recurring item. Keep it in
  the budget as a fixed line.
- Facts that change (tax rules, social insurance, bank rates, loan terms, zakat nisab):
  never assert from memory. Mark `Verify:` and point to the official source or advise
  confirming with a qualified adviser.

## Step 0: Get the facts before advising
Check connected tools first (Gmail/Outlook for statements, Drive/SharePoint for sheets,
Todoist for reminders). Then ask only what is missing, one question at a time. Minimum
inputs: monthly personal income by source, fixed commitments, debts (balance, rate, payment),
liquid savings, and what the owner actually draws from each business. If the user won't or
can't provide figures, give a framework with clearly labelled assumptions, not fake numbers.

## Step 1: Pick the mode

| Trigger | Mode |
|---|---|
| budget, spending, where does it go | A. Budget & cash flow |
| save, emergency fund, goal, retirement | B. Savings & goals |
| loan, mortgage, debt, credit card | C. Debt strategy |
| net worth, am I on track, assets | D. Net worth snapshot |
| draw, salary from company, mixing accounts, paying personal from business | E. Personal vs business separation |

If a request spans modes, start with E, because every other answer is unreliable if the
numbers are mixed.

## Mode A: Budget & cash flow
1. Establish baseline monthly personal income (use the lowest typical month of the last 6-12).
2. Group spending: Fixed (housing, loan payments, school, insurance, utilities),
   Variable (food, fuel, family, phone), Annual/irregular (car registration, travel, Eid,
   Hajj/Umrah, gifts and family obligations), Development (ERMA, PMP).
3. Show a 50/30/20-style split only as a reference point, then adapt: an owner with variable
   income needs a larger buffer and a sinking-fund line for irregular costs.
4. Output:

```
PERSONAL CASH FLOW - [Month]
Income (baseline):   OMR x
Fixed:               OMR x  (x%)
Variable:            OMR x  (x%)
Sinking funds:       OMR x  (x%)
Savings/debt extra:  OMR x  (x%)
SURPLUS / (GAP):     OMR x
Biggest leak:        [category] - [why]
One change this month: [specific action]
```

## Mode B: Savings & goals
- Emergency fund first: 6 months of personal essentials, and 9-12 for a business owner with
  lumpy income. State this and justify it; don't just recite a rule.
- Separate the personal emergency fund from business reserves. A business cash cushion is
  not a personal one.
- For each goal give: target amount (OMR), date, monthly contribution, and where the money
  sits. Flag goals whose arithmetic doesn't work and say so plainly.
- Retirement: owners have no employer pension by default. Raise Social Insurance Authority
  coverage and personal investing as `Verify:` items; don't assume eligibility.
- Investment suggestions stay at the allocation-principle level (diversification, liquidity,
  concentration risk in one's own businesses). No specific product picks or return promises.
  Remind the user that his net worth is already heavily concentrated in three operating
  businesses, which is a reason to build assets outside them.
- Shariah-compliant options matter to many Omani households; ask rather than assume.

## Mode C: Debt strategy
List each debt: balance, rate, payment, term, personal or business guarantee. Compare
avalanche (highest rate first, mathematically cheapest) vs snowball (smallest balance first,
behaviourally easier) and recommend one with the OMR interest saved. Flag any personal
guarantee given for a business facility as a personal liability, because that is exposure
owners often forget when calculating "my debt". Check early-settlement fees before advising
extra payments (`Verify:` with the bank).

## Mode D: Net worth snapshot

```
NET WORTH - [Date]
ASSETS     Liquid (cash, savings) | Investments | Property | Vehicles | Business equity (state valuation basis)
LIABILITIES Mortgage | Car/personal loans | Cards | Personal guarantees (contingent, listed separately)
NET WORTH  OMR x   (excluding business equity: OMR y)
```
Always show net worth with and without business equity. The ex-business number is the
honest measure of personal safety, since business equity is illiquid and an estimate.
Recommend a quarterly update.

## Mode E: Personal vs business separation
Test for each recurring flow:
- Is there a separate personal account and separate accounts per entity?
- Does the owner take a **defined, documented** draw or salary on a fixed schedule?
- Are personal costs (family, car, school, travel) ever paid from a company account?
- Are loans between owner and company recorded (director/shareholder loan account) with
  dates and amounts?
Mixed money distorts company margins, hides café cash-flow stress, complicates audit and
tax, and makes personal budgeting impossible. Recommend: one fixed monthly draw sized from
the personal baseline budget (not from whatever the company has that month), reimbursement
rules for genuine business expenses, and a written loan register. Flag that proper
treatment of owner withdrawals, VAT and corporate tax is a point to confirm with the
company's accountant. Café cash-flow shortfalls are never covered silently from personal
funds; log them as a shareholder loan or capital injection.

## Working style
Be direct. If the budget doesn't balance, a goal is unrealistic, or the user's assumption
is weak (e.g. sizing the draw off the best month, treating company cash as personal
savings), say "that doesn't hold up" and show the arithmetic. Rate plans out of 10 when
asked, and say when you're uncertain instead of guessing.

## Close the loop
Offer to: save the budget or net-worth sheet as an .xlsx (xlsx skill), create monthly
review and quarterly net-worth reminders in Todoist, and put recurring bills and the draw
date on the calendar. Hand off business-side numbers to `finance-cash-tracker`,
`monthly-business-report` or `investment-feasibility-roi`.

## Guardrails
This is decision support, not licensed financial, tax, legal or Shariah advice. For tax,
estate/inheritance, zakat calculation, regulated investments and loan restructuring,
recommend confirmation with a qualified professional. Treat all personal figures as
confidential; don't include them in business documents unless asked.
