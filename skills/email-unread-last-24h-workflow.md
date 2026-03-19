# Email Unread Last-24h Workflow

## Purpose
Standard procedure to fetch and present unread emails from the last 24 hours using Microsoft Graph, building on the `email-checking` and `email-search` skills.

## Steps
1. **Identify mailbox**
   - Default to the signed-in user (`/me`).
   - For shared or specific mailboxes, use `/users/{user-id}/messages`.

2. **Build time window**
   - Compute `now` in UTC and subtract 24 hours.
   - Format as ISO 8601 (e.g., `2026-01-01T12:34:56Z`).

3. **Call Microsoft Graph**
   - Auth: `DefaultAzureCredential` with `Mail.Read` scope.
   - Endpoint: `GET https://graph.microsoft.com/v1.0/me/messages` (or `/users/{user-id}/messages`).
   - Use OData parameters:
     - `$filter=isRead eq false and receivedDateTime ge {timestamp-24h}`
     - `$orderby=receivedDateTime desc`
     - `$select=sender,subject,receivedDateTime,bodyPreview,flag,importance`
     - `$top=50` (or configurable).

4. **Triage & summarise**
   - Derive urgency:
     - **Action Required**: high importance, flagged, or imperative language in subject (e.g., "please", "urgent", "action").
     - **FYI**: neutral tone, informational keywords ("update", "report", "newsletter").
     - **Low Priority**: clear marketing/newsletter patterns.
   - Produce a one-line summary from `bodyPreview`.

5. **Output format**
   - Follow the `email-checking` skill format:

   ```
   ### Action Required
   1. **From:** sender — **Subject:** subject — **Received:** date
      Summary: …
      Suggested action: …

   ### FYI
   …

   ### Low Priority
   …
   ```

## Integration Notes
- This workflow relies only on the Microsoft Graph patterns already documented in `email-checking` and `email-search` skills.
- No additional endpoints beyond those skills are introduced.
