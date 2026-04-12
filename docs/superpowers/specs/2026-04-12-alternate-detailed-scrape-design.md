# Alternate Detailed Scrape Design

Date: 2026-04-12

## Goal

Add an alternate detailed scrape flow that:

- uses a different keyword list
- uses a different `TARGET_CHAT_ID` for Telegram delivery
- runs on a different GitHub Actions schedule
- keeps the alternate scraping code isolated on a separate git branch
- still runs automatically even though GitHub scheduled workflows only trigger from the default branch

## Constraints

- The repository default branch remains `main`.
- Existing detailed scrape automation on `main` must continue to work unchanged.
- GitHub Actions schedule must live on `main`.
- The alternate implementation must be editable on its own branch without changing the current production branch logic.
- Existing secrets and runtime setup should be reused where possible.

## Approaches Considered

### Recommended: Schedule on `main`, execute code from alternate branch

Create a second workflow file on `main` with its own cron schedule. In that workflow, use `actions/checkout` to fetch the alternate branch instead of `main`, then run the scraper from that checked-out branch.

Pros:

- works with GitHub Actions scheduled workflow behavior
- keeps alternate scraper logic isolated on its own branch
- avoids changing repository default branch
- keeps operational separation clear

Cons:

- workflow config on `main` and scraper code on the alternate branch must stay coordinated

### Alternative: Put both scraper variants on `main`

Move branch-specific settings into separate scripts or config files and schedule both workflows directly from `main`.

Pros:

- simpler operationally
- no cross-branch checkout

Cons:

- does not satisfy the preference to keep alternate code on a different branch
- increases risk of accidental coupling between the two scrape variants

### Alternative: Make the alternate branch the default branch

Pros:

- GitHub schedule would run directly from that branch

Cons:

- disrupts the current repository workflow
- not aligned with the stated preference

## Selected Design

The selected design is to keep the alternate scraper implementation on a separate branch and create a second scheduled workflow on `main` that checks out that branch before running the job.

### Branch Layout

- `main` keeps the current scrape workflow and current scraper behavior.
- A new alternate branch holds the modified scraper code for:
  - alternate keyword list
  - alternate `TARGET_CHAT_ID`
  - any optional naming changes that make logs and maintenance clearer

### Workflow Layout

Add a new workflow file on `main`, for example:

`/.github/workflows/detailed_scrape_multiprocess_alt.yml`

This workflow will:

1. trigger on the alternate schedule
2. allow manual execution with `workflow_dispatch`
3. check out the alternate branch explicitly
4. install the same Python and browser dependencies as the existing detailed multiprocess workflow
5. run `python detailed_scrape_multi.py --debug` from the alternate branch contents

### Schedule

The existing detailed multiprocess schedule is:

- `30 16 * * *` = 23:30 WIB
- `40 1 * * *` = 08:40 WIB
- `15 6 * * *` = 13:15 WIB
- `45 8 * * *` = 15:45 WIB

The alternate workflow will run 45 minutes earlier:

- `45 15 * * *` = 22:45 WIB
- `55 0 * * *` = 07:55 WIB
- `30 5 * * *` = 12:30 WIB
- `0 8 * * *` = 15:00 WIB

Comments should be added in the workflow to show the Jakarta times for readability.

## Code Changes

### On the alternate branch

Update `detailed_scrape_multi.py` so that:

- `keywords` contains the alternate list
- `TARGET_CHAT_ID` points to the alternate Telegram destination

If the single-process script `detailed_scrape.py` is still used for manual fallback or debugging, mirror the same values there to avoid confusion.

### On `main`

Add a new workflow file that is based on the existing `detailed_scrape_multiprocess.yml` but uses:

- the alternate cron schedule
- `actions/checkout` configured with the alternate branch ref
- a distinct workflow name so runs are easy to distinguish in GitHub Actions

## Data Flow

1. GitHub Actions scheduler on `main` triggers the alternate workflow.
2. The workflow runner checks out the alternate branch.
3. The runner installs dependencies and browser tooling.
4. The alternate branch version of `detailed_scrape_multi.py` runs.
5. Results are processed using the alternate keyword set.
6. Telegram notifications are sent to the alternate `TARGET_CHAT_ID`.

## Error Handling

- If the alternate branch is renamed or deleted, the workflow will fail at checkout.
- If secrets differ between the two flows in the future, the workflow should be updated explicitly rather than assuming parity.
- If Telegram permissions are not configured for the alternate chat, the existing bot access check in `detailed_scrape_multi.py` should fail fast.
- If the alternate schedule overlaps too closely with the current workflow, jobs may queue longer; this is acceptable because each workflow runs independently on GitHub-hosted runners.

## Testing Plan

Before enabling the schedule:

1. create the alternate branch
2. update the alternate branch scraper values
3. push the alternate branch to origin
4. add the new workflow file on `main`
5. trigger the new workflow manually with `workflow_dispatch`
6. confirm the workflow checks out the alternate branch
7. confirm the correct Telegram destination receives the message
8. confirm no regression to the existing detailed multiprocess workflow

## Implementation Notes

- Use a clear branch name such as `detailed-scrape-alt`.
- Use a clear workflow name such as `Detailed Scrape Multiprocess Alt`.
- Keep comments in the workflow that map UTC cron to WIB to reduce scheduling mistakes later.
- Avoid changing unrelated workflow behavior while introducing the alternate flow.
