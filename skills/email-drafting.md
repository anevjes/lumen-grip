# Email Drafting

## Purpose
Help the user compose clear, professional email replies and new messages.

## Guidelines
1. **Tone** — Match the formality of the original thread. Default to professional but concise.
2. **Structure** — Use short paragraphs. Lead with the key point or ask, then provide supporting detail.
3. **Action items** — If the email requires something from the recipient, state it explicitly with a deadline if applicable.
4. **Reply vs. new** — When replying, reference the original subject and relevant context. When composing new, include a clear subject line.
5. **Review** — Flag anything that could be misread or is missing (attachments mentioned but not listed, unanswered questions).

## Output Format
```
**To:** recipient
**Subject:** subject line
**Body:**
…
```

## Integration Notes
- To send via Microsoft Graph: `POST https://graph.microsoft.com/v1.0/me/sendMail`
- To create a draft: `POST https://graph.microsoft.com/v1.0/me/messages`
- Required scope: `Mail.Send` (send) or `Mail.ReadWrite` (draft).
