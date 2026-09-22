# MVP scope

## Problem

Personal notes and documents are hard to search when information is spread across files. Jarvis Lite should answer questions about an uploaded document collection and show where each answer came from.

## First release

- Upload PDF, Markdown, and plain text files.
- Extract text, split it into chunks, and store embeddings in PostgreSQL with `pgvector`.
- Ask a question and retrieve relevant chunks.
- Generate an answer grounded in those chunks, with a document name and location for each cited passage.
- Show the answer and its sources in a React interface.
- Save conversations so a user can reopen them.

## Acceptance criteria

1. A user can upload a supported file and see whether ingestion succeeded or failed.
2. A question about uploaded content returns an answer with source references that can be checked against the original document.
3. If the documents do not support an answer, the assistant says so instead of inventing a citation.
4. A user can reopen a previous conversation.

## Later milestones

- A bounded agent loop with validated tool arguments and clear error handling.
- Document search, calculator, and read-only access to the finance dashboard as tools.
- A fixed evaluation set measuring retrieval and answer quality, plus logging of latency, tokens, and cost.
- Automated tests, Docker, CI, and deployment.

The ML transaction classifier belongs in the existing `fullstack-finance-dashboard` repository. Fine-tuning, voice, and multi-agent workflows are separate later experiments.
