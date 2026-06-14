---
description: Enforces an opinionated/bold writing tone when creating, editing, or
  rewriting project documentation files. Applies to README.md, CONTRIBUTING.md, CHANGELOG.md,
  mkdocs pages, vitepress content, and similar documentation — not code comments,
  docblocks, or inline code docs.
name: documentation-tone
---

## When This Skill Applies

This skill triggers **only** when the task involves creating, editing, or rewriting **project documentation files**, including but not limited to:

- Root-level docs: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE.md`, `SECURITY.md`
- Documentation site content: mkdocs pages, vitepress pages, Sphinx `.rst` files, Docusaurus `.mdx` files
- Any `.md`, `.mdx`, `.rst`, or `.txt` file inside a `docs/` or documentation directory

**This skill does NOT apply to:**

- Code comments
- Docblocks or docstrings
- Inline code documentation
- API doc generators (auto-generated output)

---

## Writing Tone: Opinionated / Bold

All documentation covered by this skill MUST be written in an **opinionated and bold** tone. Follow these rules without exception:

1. **State positions clearly and unapologetically.** Minimal hedging. Drop words like "might," "perhaps," "it could be argued." If something is true, say it.

2. **Use direct, active language.** No passive voice padding. "Byte validates every change" — not "Every change is validated by Byte."

3. **Be concise.** Say what needs to be said, then stop. Every sentence must earn its place.

4. **Frame trade-offs as deliberate design choices.** Never apologize for what the project doesn't do. "We chose X because Y" — not "Unfortunately, X doesn't support Z."

5. **Avoid marketing fluff, defensive framing, and repetitive emphasis.** One strong statement beats three weak ones. Cut filler words and hollow superlatives.

6. **Lead with the value proposition.** One line, not a paragraph. The reader should know what they get within the first sentence.

7. **Use "you" naturally.** Address the reader directly. Write like you're talking to a peer developer, not drafting a legal document.

8. **Drop defensive language.** Instead of "X isn't for you if…," frame it positively: "Built for developers who want Y." Turn exclusions into affirmations.

---

## Structural Convention: Diátaxis (Default)

This project uses the **Diátaxis** documentation framework as its default structural model. Content falls into four categories:

| Category          | Purpose                              | Reader's Goal         |
| ----------------- | ------------------------------------ | --------------------- |
| **Tutorials**     | Learning-oriented guided experiences | "Teach me"            |
| **How-to Guides** | Task-oriented practical steps        | "Help me do X"        |
| **Explanation**   | Understanding-oriented discussion    | "Help me understand"  |
| **Reference**     | Information-oriented technical specs | "Give me the details" |

The opinionated/bold writing tone applies **across all four Diátaxis categories** and across any other structural style the project may configure. Tone and structure are independent — this skill governs tone only.
