> **Customize this file**: Tailor this template to your project by noting specific contribution types you're looking for, adding a Code of Conduct, or adjusting the writing guidelines to match your style.

# Contribute to the documentation

Thank you for your interest in contributing to our documentation! This guide will help you get started.

## How to contribute

### Option 1: Edit directly on GitHub

1. Navigate to the page you want to edit
2. Click the **Edit this file** button (the pencil icon)
3. Make your changes and submit a pull request

### Option 2: Local development

1. Fork and clone this repository
2. Install the Mintlify CLI: `npm i -g mint`
3. Create a branch for your changes
4. Make changes
5. Navigate to the docs directory and run `mint dev`
6. Preview your changes at `http://localhost:3000`
7. Commit your changes and submit a pull request

## Writing guidelines

- **Use active voice**: "Run the command" not "The command should be run"
- **Address the reader directly**: Use "you" instead of "the user"
- **Keep sentences concise**: Aim for one idea per sentence
- **Lead with the goal**: Start instructions with what the user wants to accomplish
- **Use consistent terminology**: Don't alternate between synonyms for the same concept
- **Include examples**: Show, don't just tell

## Navigation and UI instructions

When you tell a reader how to move through the product UI, follow one format. The
goal is a path a reader can follow literally, label for label, in order, the way
a screen reader user would read it aloud. Accuracy first, then consistency.

### Format

- **Separator.** Join steps in a path with `→` (a real right arrow, U+2192) with
  one space on each side. Do not use `>`, `->`, `/`, `»`, or `›`.
- **Labels.** Bold every clickable UI label exactly as it appears on screen:
  `**Settings** → **Repositories**`.
- **Placeholders.** Put variable steps in bold brackets: `**[your repository]**`.
- **Element type.** Name the kind of control when it is not obvious from context:
  the **Merge Queue** tab, the **Save** button, toggle **GitHub Comments** off,
  the **[repository]** dropdown. Use: tab, button, toggle, dropdown, menu, link.
- **Whose UI.** When it could be confused, say where you are: "In the Trunk app,
  navigate to…" or "In GitHub, navigate to…". The arrow format is the same in
  both.

### Verbs

Use one verb per action and do not alternate:

| Verb | Use for |
| --- | --- |
| **Navigate to** | A multi-step path through menus or settings (uses arrows). |
| **Click** | A single button or link. |
| **Select** | Choosing an option from a list or dropdown. |

Retire: *Go to*, *Head to*, *Open the…*, *Choose*.

### Example

> Open the **Merge Queue** tab, then navigate to **Settings** → **Repositories**
> → **[your repository]** → **Merge Queue**. Click **Save**.

### Accuracy

A path that reads cleanly can still be wrong. UI changes, settings move, labels
get renamed. Before you write or edit a navigation path, confirm it against the
live product. Walk the exact path yourself. If you cannot confirm a step, flag it
for review rather than guessing.
