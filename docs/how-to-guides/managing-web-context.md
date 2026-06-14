# Manage Web Context

**Category**: How-to Guide

This guide shows you how to add, view, and remove web pages from your session context. Web pages become available to the AI during your conversation, letting you reference external documentation, articles, and guides without copying content manually.

## Prerequisites

- Byte installed on your system
- Web features enabled in your `.byte/config.jsonc`
- A URL you want to add to context

## Step 1: Enable Web Features

Before you can scrape and add web pages, enable web commands in your configuration.

Open `.byte/config.jsonc` and add or update the `web` section:

```jsonc
{
  "web": {
    "enable": true,
    "chrome_binary_location": "/path/to/chrome"
  }
}
```

The two required fields are:

- **`enable`** — Set to `true` to activate web scraping
- **`chrome_binary_location`** — Full path to your Chrome or Chromium binary

### Finding Your Chrome Binary

**On macOS:**

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
```

Or if you use Chromium:

```bash
/Applications/Chromium.app/Contents/MacOS/Chromium
```

**On Linux:**

```bash
/usr/bin/google-chrome
# or
/usr/bin/chromium-browser
```

**On Windows:**

```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

Copy the full path into your config and save. Byte will validate it on startup.

## Step 2: Understand Web Scraping

When you add a web page to context, Byte:

1. **Launches a headless Chrome browser** — Opens the page without a GUI
2. **Waits for content to load** — Ensures JavaScript-rendered content is captured
3. **Detects the site type** — Sphinx, GitBook, GitHub, MkDocs, or generic HTML
4. **Applies site-specific parsing** — Extracts the most relevant content (navigation removed, ads stripped)
5. **Converts to markdown** — HTML is transformed into clean, readable markdown
6. **Shows you the result** — Displays the scraped content for review
7. **Asks for confirmation** — Only adds it to context if you approve

This process ensures you get clean, readable content without boilerplate or noise.

## Step 3: Add a Web Page with `/context`

The simplest way to add a web page is the smart `/context` command, which auto-detects whether you're adding a file or URL:

```bash
/context https://docs.example.com/api-reference
```

This command:

1. Detects the URL (starts with `http://` or `https://`)
2. Launches the browser and scrapes the page
3. Auto-detects the site type (Sphinx, GitBook, etc.) and applies appropriate parsing
4. Displays the scraped content in a formatted panel
5. Prompts: "Add this content to the LLM context?"
6. If you answer **Yes**, adds it to context; if **No**, discards it

### Example: Add Multiple URLs

```bash
/context https://docs.example.com/api
/context https://docs.example.com/guides
```

Each URL is scraped, shown, and you confirm each one separately.

## Step 4: Add a Web Page Directly with `/web`

For explicit web operations, use the direct `/web` command:

```bash
/web https://docs.example.com/tutorial
```

This is identical to `/context` for URLs. Use this when you want to be explicit, or when you're adding multiple URLs in rapid succession.

### Add Multiple URLs at Once

The `/web` command accepts multiple URLs separated by spaces, commas, or newlines:

```bash
/web https://docs.example.com/api https://docs.example.com/guide
```

Or:

```bash
/web https://docs.example.com/api, https://docs.example.com/guide, https://docs.example.com/faq
```

Each URL is scraped, displayed, and you confirm each one independently before it's added to context.

### Valid URL Formats

URLs must start with `http://` or `https://`:

```bash
/web https://github.com/user/repo  # ✓ Valid
/web http://example.com            # ✓ Valid
/web example.com                    # ✗ Invalid (missing scheme)
```

## Step 5: Review Scraped Content

After you add a URL, Byte scrapes the page and displays the result:

```
╭──────────────────────────────────────────────────╮
│ Content: https://docs.example.com/api-reference │
├──────────────────────────────────────────────────┤
│                                                  │
│ # API Reference                                 │
│                                                 │
│ ## Authentication                               │
│ POST /auth/login                                │
│ ...                                             │
│                                                 │
╰──────────────────────────────────────────────────╯

? Add this content to the LLM context?

❯ Yes
  No
```

Review the markdown content. If it looks good, select **Yes**. If the parsing missed important content or included too much noise, select **No** and try a different approach (e.g., adding a more specific URL).

## Step 6: Site Type Auto-Detection

Byte automatically detects which type of documentation site you're scraping and applies the best parsing strategy:

- **Sphinx** — Python documentation sites (removes navigation, sidebars)
- **GitBook** — Technical documentation platforms (extracts main content)
- **GitHub** — Repository READMEs and wikis (cleans markdown)
- **MkDocs** — Material-themed documentation (removes theme chrome)
- **Generic** — Fallback for standard HTML (best-effort extraction)

You don't need to do anything — detection is automatic. If parsing isn't optimal for a particular site, you can try a different URL (e.g., add a more specific page instead of the homepage).

## Step 7: List All Context Items

View everything currently in your session context, including both files and web pages:

```bash
/ctx:ls
```

Output shows all items by key:

```
╭────────────────────────────────────────────────────────╮
│ Session Context Items (4)                              │
├────────────────────────────────────────────────────────┤
│ src/byte/config.py                                     │
│ https-docs-example-com-api                             │
│ https-docs-example-com-guide                           │
│ pyproject.toml                                         │
╰────────────────────────────────────────────────────────╯
```

Web context keys are generated from the URL (slugified for readability). File context keys match the file paths you added.

## Step 8: Remove Web Context Items

Use the same `/ctx:drop` command to remove web pages:

### Remove a Specific Web Page by Key

```bash
/ctx:drop https-docs-example-com-api
```

Byte confirms: "Removed https-docs-example-com-api from session context"

### Remove Multiple Items Interactively

```bash
/ctx:drop
```

A menu appears with all context items (files and web pages). Select the ones you want to remove and press Enter.

### Why Remove Items?

Web content can be large and consume many tokens. Remove pages you've finished referencing to keep context efficient.

## Step 9: How Web Context Reaches the AI

When you send a message, Byte automatically injects all context items (both files and web pages) into the AI's prompt. Each web page is wrapped with metadata tags:

```
<session_context type="web" key="https-docs-example-com-api">
[web page markdown here]
</session_context>
```

The AI can see all web pages in context and reference them by key. You don't need to manually include URLs in your prompt — the actual content is already available.

## Step 10: Understand Persistence

**Session persistence:** Web content is stored in `.byte/session_context/` on your disk as markdown files. They persist across prompts within the same session.

**Session boundaries:** When you end your session and start a fresh one, web context is cleared. You need to re-add URLs if you want them in the new session.

To start fresh immediately:

```bash
/ctx:drop
# Select all items and confirm removal
```

Then add the URLs you need for the current task.

## Combining File and Web Context

You can mix file and web context seamlessly. Add source code files and external documentation:

```bash
/context src/byte/cli.py
/context https://docs.python.org/cli-argparse
/ctx:ls  # Shows both types together
```

Both are injected into the AI's prompt when you send a message, letting you reference internal and external knowledge in one conversation.

## Common Workflows

### Learning a New Framework

Add the framework documentation:

```bash
/web https://docs.framework.com/getting-started
/web https://docs.framework.com/api-reference
```

Ask the AI to explain concepts or help you build examples. The AI has the official docs in context.

### Bug Hunting in Third-Party Libraries

Add your code and the library's documentation:

```bash
/context src/my_app/handler.py
/web https://github.com/library/repo/blob/main/README.md
/web https://library-docs.com/troubleshooting
```

Describe the issue. The AI can see your code and the library docs together.

### API Integration

Add your service code and the external API documentation:

```bash
/context src/services/payment_service.py
/web https://api.payment-provider.com/docs
/web https://api.payment-provider.com/authentication
```

Ask the AI to review your integration or help debug API calls. All relevant docs are available.

### Documentation Review

Add your docs and related API docs:

```bash
/context docs/api.md
/web https://openapi-spec.io/
```

Ask the AI to improve your documentation against industry standards. It sees both.

## Troubleshooting

### "Web commands are not enabled"

Check your `.byte/config.jsonc`:

```jsonc
{
  "web": {
    "enable": true,
    "chrome_binary_location": "/path/to/chrome"
  }
}
```

Make sure `enable` is `true` and the Chrome path is valid.

### Scraped Content Looks Wrong

The page might use heavy JavaScript or non-standard HTML. Try:

1. Adding a more specific URL (e.g., `/docs/api` instead of `/`)
2. Removing the page and using a different documentation source
3. Adding relevant source code files instead and letting the AI reference those

### Chrome Binary Not Found

Double-check the path:

```bash
ls -la /path/to/chrome  # macOS / Linux
where chrome            # Windows
```

Copy the exact path from the output into your config.

## Next Steps

Now that you can manage web context, combine it with file context to build rich, multi-source conversations. For advanced context workflows, see the explanation section on how context is structured and injected into prompts.

