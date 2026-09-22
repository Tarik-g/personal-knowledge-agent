# Jarvis Lite: first-release scope

## Problem

It is hard to find and verify information inside a PDF. Jarvis Lite should answer a question about one uploaded PDF and show the passage that supports the answer.

## User flow

1. Upload one text-based PDF in the React interface.
2. The FastAPI backend validates the file and extracts text with page numbers.
3. The backend splits the text into chunks, creates embeddings, and stores them in PostgreSQL with `pgvector`.
4. Ask a question about that PDF. The backend retrieves relevant chunks and uses them to generate an answer.
5. See the answer with the PDF filename, page number, and a supporting excerpt for each source.

## First-release boundaries

- One PDF per question; no search across a document collection yet.
- Text-based PDFs only. Scanned PDFs requiring OCR are a later extension.
- No login, conversation history, Markdown/text upload, finance integration, agent tools, or autonomous actions in this release.
- Development and verification run locally first. Deployment comes after the quality milestones.
- The model and embedding provider will be selected before those steps are implemented, considering cost and whether document content may leave the local machine.

## Acceptance criteria

1. A text-based PDF can be uploaded, and the interface shows whether processing succeeded.
2. An unsupported, unreadable, or image-only file produces a clear error.
3. A question answered from the PDF shows a filename, page number, and excerpt that can be checked in the original PDF.
4. When the retrieved passages do not support an answer, the assistant says that it cannot find the answer in the PDF and does not fabricate a source.
5. A small end-to-end example and automated checks demonstrate the successful path and the main error cases.

## Build order

1. Define the scope and start the API (done).
2. Upload validation and page-aware text extraction.
3. Chunking with page metadata.
4. PostgreSQL, `pgvector`, embeddings, and retrieval.
5. Answer generation and source handling.
6. React upload and question interface.
7. Verify the full flow and document the result.

For each step, we briefly explain the purpose, implement one small piece, check its behavior, and review what was learned before moving on.

## Later milestones

- A bounded agent loop with function calling, validated tool arguments, timeouts, and clear error handling.
- Document search, calculator, and read-only access to the finance dashboard as tools.
- A fixed evaluation set measuring retrieval and answer quality; prompt-injection checks; logging of latency, tokens, and cost.
- Conversation history and broader file support, if useful after the first release.
- Docker, CI, and cloud deployment.

The ML transaction classifier is a separate project in the existing `fullstack-finance-dashboard` repository. This repository does not change the finance dashboard. Fine-tuning, voice, and multi-agent workflows are separate later experiments.
