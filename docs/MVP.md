# Jarvis Lite: first-release scope

## Problem

It is hard to find and verify information inside a PDF. Jarvis Lite should answer a question about one uploaded PDF and show the passage that supports the answer.

## User flow

1. Upload one text-based PDF in the React interface.
2. The FastAPI backend validates the file and extracts text with page numbers.
3. The backend splits the text into chunks and creates local embeddings.
4. The backend retrieves the most relevant chunks for the question.
5. The local Qwen3 model formulates an answer from those chunks only.
6. See the answer with the PDF filename, page number, and a supporting excerpt for each source.

The current implementation sends the PDF with every question and does not persist it. The next iteration stores the document and its embeddings in PostgreSQL so the same PDF can be questioned repeatedly.

## First-release boundaries

- One PDF per question; no search across a document collection yet.
- Text-based PDFs only. Scanned PDFs requiring OCR are a later extension.
- No login, conversation history, Markdown/text upload, finance integration, agent tools, or autonomous actions in this release.
- Each anonymous browser has its own temporary document space. All reads and retrieval queries must be scoped to that browser's session, and idle data is removed after 24 hours.
- Development and verification run locally first. The final portfolio demo must be publicly reachable without Docker on the visitor's machine.
- Embeddings use the local multilingual MiniLM model through FastEmbed. Answers use the local `qwen3:1.7b` model through Ollama. PDF passages stay on the machine during both steps, and neither step has a per-request API charge.

## Acceptance criteria

1. A text-based PDF can be uploaded, and the interface shows whether processing succeeded.
2. An unsupported, unreadable, or image-only file produces a clear error.
3. A question answered from the PDF shows a filename, page number, and excerpt that can be checked in the original PDF.
4. When the retrieved passages do not support an answer, the assistant says that it cannot find the answer in the PDF and does not fabricate a source.
5. A small end-to-end example and automated checks demonstrate the successful path and the main error cases.
6. A public demo URL supports the complete upload, question, and cited-answer flow.
7. Uploading a PDF in browser A does not expose it to browser B, including through document lists or questions.

## Build order

1. Define the scope and start the API (done).
2. Upload validation and page-aware text extraction (done).
3. Chunking with page metadata (done).
4. Local embeddings and semantic retrieval (done).
5. Local answer generation and source handling (done).
6. React upload and question interface (done).
7. Persist documents and embeddings with PostgreSQL and `pgvector` (next).
8. Add retrieval evaluation and calibrate the no-answer threshold.
9. Deploy without requiring Docker on the visitor's machine and document the public demo.

For each step, we briefly explain the purpose, implement one small piece, check its behavior, and review what was learned before moving on.

## Later milestones

- A bounded agent loop with function calling, validated tool arguments, timeouts, and clear error handling.
- Document search, calculator, and read-only access to the finance dashboard as tools.
- A fixed evaluation set measuring retrieval and answer quality; prompt-injection checks; logging of latency, tokens, and cost.
- Conversation history and broader file support, if useful after the first release.
- CI and deployment improvements.

The ML transaction classifier is a separate project in the existing `fullstack-finance-dashboard` repository. This repository does not change the finance dashboard. Fine-tuning, voice, and multi-agent workflows are separate later experiments.
