# ResumeForge 📄

An AI-powered Resume Tailoring System that analyzes job descriptions 
against your career profile using Natural Language Processing and 
generates ATS-optimized PDF resumes automatically.

## Features
- 🔬 TF-IDF cosine similarity scoring (0–100 ATS match score)
- 🎯 Missing and matching keyword analysis
- 📄 One-click ATS-compliant PDF generation
- ⚡ Async task processing with Celery + Redis
- 🔐 Secure multi-user architecture with UUID-based records

## Tech Stack
Django 5.1 · Python 3.12 · scikit-learn · spaCy · 
WeasyPrint · Celery · Redis · PostgreSQL · Tailwind CSS

## Quick Start
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
python manage.py migrate
python manage.py runserver
```
