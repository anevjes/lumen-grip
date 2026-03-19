# Email Search

## Purpose
Help the user find specific emails using targeted search queries.

## Guidelines
1. **Clarify the search** — Ask for any combination of: sender, recipient, subject keywords, body keywords, date range, has-attachment, folder.
2. **Build the query** — Translate the user's intent into the most efficient search filter.
3. **Present results** — Show matching emails in reverse-chronological order with: sender, subject, date, and a one-line preview.
4. **Refine** — If too many results, suggest narrowing criteria. If zero results, suggest broadening or alternative keywords.

## Microsoft Graph Search Patterns
```
# KQL-style search (preferred for keyword/body searches)
POST https://graph.microsoft.com/v1.0/me/messages?$search="keyword"

# OData filter (preferred for structured queries)
GET https://graph.microsoft.com/v1.0/me/messages?$filter=from/emailAddress/address eq 'sender@example.com' and receivedDateTime ge 2026-01-01T00:00:00Z&$orderby=receivedDateTime desc&$top=10

# Combine folder + filter
GET https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$filter=hasAttachments eq true
```

## Output Format
```
### Search results for: "<query>"
Found N emails.

1. **From:** sender — **Subject:** subject — **Date:** date
   Preview: first line of body…
2. …
```
