# Flaky Tests: Linear Field Defaults and Link Existing Tickets

**May 19, 2026** · Flaky Tests

This week's update makes the Linear ticketing integration faster to configure and more flexible when you already have tickets tracking a flaky test.

## New features

### Field defaults for auto-created Linear tickets

When you connect a Linear team in **Settings > Repositories > Ticketing Integration**, you can now set per-repository defaults that pre-populate every new ticket:

- **Priority** — Urgent, High, Medium, Low, or No priority
- **Labels** — one or more team- or workspace-level labels
- **Estimate** — matches your team's scale (Fibonacci, T-shirt, linear, or exponential)
- **Project** — filtered to projects accessible by the selected team
- **Assignee** — chosen from team members

Defaults are applied whenever you open the **Create Ticket** modal and can still be overridden before submitting. Switching teams clears and reloads the available options automatically.

[Read the docs →](https://docs.trunk.io/flaky-tests/management/ticketing/linear-integration#field-defaults)

### Link existing Linear tickets to a test

If you already have a Linear ticket tracking a flaky test, you can attach it without creating a duplicate. From the Test Details page, click **Link Ticket**, paste the Linear URL or ID, and submit. The ticket's title, status, and assignee sync back from Linear.

You can also link tickets programmatically with the [Link Ticket to Test Case API](https://docs.trunk.io/flaky-tests/reference/api-reference#post-flaky-tests-link-ticket-to-test-case).

[Read the docs →](https://docs.trunk.io/flaky-tests/management/ticketing/linear-integration#link-existing-tickets-to-tests)
