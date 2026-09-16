# DocuMind – AI Document Intelligence & RAG Platform

DocuMind is a full-stack AI-powered document intelligence platform that allows users to upload documents, process their content, and ask natural-language questions about the uploaded documents.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant document content and provide context-aware answers instead of relying only on the language model's general knowledge.

## Live Application

Frontend: https://YOUR-VERCEL-URL

Backend API: https://documind-backend-cxcf.onrender.com

## Features

- User registration and login
- JWT-based authentication
- Secure document upload
- PDF and DOCX document processing
- Automatic text extraction
- Document chunking for efficient retrieval
- Vector embeddings using NVIDIA NIM
- PostgreSQL database with pgvector
- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Context-aware question answering
- Source references for generated answers
- User-specific document access
- Document status tracking
- Document deletion
- Responsive React interface

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Gunicorn
- JWT Authentication

### Database & Storage
- PostgreSQL
- Supabase
- pgvector
- Supabase Storage

### AI
- NVIDIA NIM
- NVIDIA Nemotron Embeddings
- Retrieval-Augmented Generation (RAG)

### Deployment
- Vercel – Frontend
- Render – Backend
- Supabase – Database and Storage
- GitHub – Source Code

## System Architecture

```text
                         User
                          |
                          v
                 React + Vite Frontend
                       (Vercel)
                          |
                          | REST API
                          v
                  Flask Backend
                    (Render)
                          |
             +------------+------------+
             |                         |
             v                         v
       Supabase PostgreSQL       Supabase Storage
       + pgvector                Document Files
             |
             v
      Document Chunks
       + Embeddings
             |
             v
       NVIDIA NIM APIs
       Embeddings + LLM