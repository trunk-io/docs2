# Mintlify Starter Kit

Use the starter kit to get your docs deployed and ready to customize.

Click the green **Use this template** button at the top of this repo to copy the Mintlify starter kit. The starter kit contains examples with

- Guide pages
- Navigation
- Customizations
- API reference pages
- Use of popular components

**[Follow the full quickstart guide](https://starter.mintlify.com/quickstart)**

## AI-assisted writing

Set up your AI coding tool to work with Mintlify:

```bash
npx skills add https://mintlify.com/docs
```

This command installs Mintlify's documentation skill for your configured AI tools like Claude Code, Cursor, Windsurf, and others. The skill includes component reference, writing standards, and workflow guidance.

See the [AI tools guides](/ai-tools) for tool-specific setup.

## Development

Install the [Mintlify CLI](https://www.npmjs.com/package/mint) to preview your documentation changes locally. To install, use the following command:

```
npm i -g mint
```

Run the following command at the root of your documentation, where your `docs.json` is located:

```
mint dev
```

View your local preview at `http://localhost:3000`.

## Publishing changes

Install our GitHub app from your [dashboard](https://dashboard.mintlify.com/settings/organization/github-app) to propagate changes from your repo to your deployment. Changes are deployed to production automatically after pushing to the default branch.

## PR labels

PRs in this repo are tagged by automated workflows that verify each doc change against the underlying product state. Labels fall into three groups.

### Feature lifecycle (set by `verify-docs-pr`)

Exactly one of these is applied to every docs PR. They reflect whether customers can actually use the feature being documented.

| Label | Color | Meaning |
|---|---|---|
| `ready to merge` | green | Customers can use this. Ready to publish. |
| `staged` | yellow | On in staging only. Re-run verify after prod rollout. |
| `pending` | orange | Eng merged but flag off in prod. Hold off. |
| `awaiting eng` | red | Eng PR not merged. Hold. |

### Code verification (set by `verify-docs-against-code`)

Applied when the PR's factual claims are checked against trunk-io source. Exactly one is set when verify runs.

| Label | Color | Meaning |
|---|---|---|
| `code-verified` | green | All factual claims confirmed in source. |
| `code-verified-partial` | yellow | Confirmed claims, some unverifiable. |
| `needs eng review` | red | At least one claim contradicts source. |

### Source / review flow

Sticky labels that mark how a PR was sourced or where it needs extra eyes. Additive — a PR can have multiple.

| Label | Color | Meaning |
|---|---|---|
| `changelog` | blue | PR touches the changelog (auto-generated drafts, hosting, formatting, indexing). |
| `needs review` | purple | PR sourced from customer-feedback-mining; needs human scrutiny for accuracy before merge. |

GitHub's default labels (`bug`, `documentation`, `enhancement`, etc.) are also present but not used in our automated workflows.

## Need help?

### Troubleshooting

- If your dev environment isn't running: Run `mint update` to ensure you have the most recent version of the CLI.
- If a page loads as a 404: Make sure you are running in a folder with a valid `docs.json`.

### Resources
- [Mintlify documentation](https://mintlify.com/docs)
