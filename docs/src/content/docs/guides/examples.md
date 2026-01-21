---
title: Example Prompts & Outputs
description: Ready-to-use prompts and sample generated documentation
---

# Example Prompts & Outputs

Copy these prompts to get started quickly with DocuGen.

## Live Example: GitHub Search

This example was generated using DocuGen with the Playwright MCP. The screenshots show smart auto-annotation in action.

**Prompt used:**
```
Document this workflow: Search for repositories on GitHub
Starting URL: https://github.com/search
Audience: beginner
```

### Step 1: Navigate to GitHub Search

![Step 1: GitHub search page with annotated search box](/claudeDocugen/examples/github-search/step-01-annotated.png)

The search box is automatically highlighted with a numbered callout and click indicator - no manual coordinates needed.

### Step 2: View Search Results

![Step 2: Search results with annotated first result](/claudeDocugen/examples/github-search/step-02-annotated.png)

The target element (first search result) is highlighted with an arrow pointing to it.

### Smart Annotation Features

DocuGen's smart annotations automatically:
- **Detect the target element** from Playwright's element metadata
- **Draw highlight boxes** around interactive elements
- **Add numbered callouts** positioned to avoid overlapping content
- **Show click indicators** for buttons, links, and inputs
- **Draw arrows** for small or hard-to-find elements
- **Handle HiDPI displays** with automatic scale factor detection

### What DocuGen Generated

DocuGen produced this complete markdown documentation:

```
# Search for Repositories on GitHub

## Prerequisites
- Web browser with internet access
- GitHub account (optional)

## Steps

### Step 1: Navigate to GitHub Search
GitHub's dedicated search page provides a clean interface...

### Step 2: Enter your search query
Type keywords that describe what you're looking for...

## Troubleshooting
**No results found** - Try broader keywords or check spelling
**Too many results** - Use filters or add qualifiers like stars:>100
```

View the [full generated documentation](/claudeDocugen/examples/github-search/github-search-guide.md).

---

## Prompt Templates

### SaaS Applications

**Slack - Invite Team Members**
```
Document this workflow: Invite new team members to Slack workspace
Starting URL: https://app.slack.com/admin
Audience: intermediate
```

**Trello - Create Board**
```
Document this workflow: Set up a new Trello board for project management
Starting URL: https://trello.com
Audience: beginner
```

**Notion - Create Database**
```
Document this workflow: Create a database in Notion
Starting URL: https://notion.so
Audience: beginner
```

### Developer Tools

**Vercel - Deploy App**
```
Document this workflow: Deploy a Next.js app to Vercel
Starting URL: https://vercel.com/new
Audience: intermediate
```

**AWS S3 - Create Bucket**
```
Document this workflow: Create an S3 bucket with public read access
Starting URL: https://console.aws.amazon.com/s3
Audience: intermediate
Note: Blur any account IDs or ARNs
```

**GitHub Actions - Set Up CI**
```
Document this workflow: Configure GitHub Actions CI/CD
Starting URL: https://github.com/myrepo/actions/new
Audience: expert
Template: quick_reference
```

### E-commerce

**Shopify - Add Product**
```
Document this workflow: Add a new product to Shopify store
Starting URL: https://admin.shopify.com/store/YOUR-STORE/products/new
Audience: beginner
```

**Stripe - Process Refund**
```
Document this workflow: Issue a refund in Stripe Dashboard
Starting URL: https://dashboard.stripe.com/payments
Audience: intermediate
Note: Blur all payment IDs and amounts
```

### HR & Admin

**Google Workspace - Add User**
```
Document this workflow: Add new employee to Google Workspace
Starting URL: https://admin.google.com/ac/users
Audience: intermediate
```

**Zoom - Schedule Meeting**
```
Document this workflow: Schedule a recurring Zoom meeting
Starting URL: https://zoom.us/meeting/schedule
Audience: beginner
```

---

## Advanced Options

### Specify Output Format
```
Document this workflow: Set up Cloudflare DNS
Starting URL: https://dash.cloudflare.com
Audience: intermediate
Output: ./docs/cloudflare-setup.md
Image format: jpg
```

### Request Redaction Review
```
Document this workflow: Configure API keys in dashboard
Starting URL: https://app.example.com/settings/api
Audience: intermediate
Note: Please ask me before blurring - some keys are examples
```

### Expert Quick Reference
```
Document this workflow: Kubernetes pod deployment
Starting URL: https://console.cloud.google.com/kubernetes
Audience: expert
Template: quick_reference
```

---

## Tips for Better Results

### Be Specific About Goals

| Less Effective | More Effective |
|----------------|----------------|
| `Document using Figma` | `Document this workflow: Create a new design file and add a frame` |
| `Help with AWS` | `Document this workflow: Create an EC2 instance with SSH access` |

### Choose the Right Audience

- **beginner**: New users, full context, all warnings
- **intermediate**: Regular users, key steps, critical warnings only
- **expert**: Power users, minimal explanation

### Mention Sensitive Data

Always specify if the workflow involves:
- API keys or tokens
- Payment information
- Personal data
- Internal URLs or IDs

DocuGen will prompt you to review detected sensitive fields before blurring.
