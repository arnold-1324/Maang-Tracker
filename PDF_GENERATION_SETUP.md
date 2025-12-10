# PDF Generation Setup Guide

## Overview
Your MAANG Tracker now uses your actual LaTeX resume and can generate professional PDFs.

## Installation Options

### Option 1: Full LaTeX Installation (Recommended for Production)

**Windows:**
```bash
# Install MiKTeX (LaTeX distribution)
# Download from: https://miktex.org/download
# Or use chocolatey:
choco install miktex

# Verify installation
pdflatex --version
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# Mac
brew install --cask mactex
```

### Option 2: Tectonic (Modern, Lightweight)

```bash
# Install Tectonic
# Windows (with Scoop)
scoop install tectonic

# Mac
brew install tectonic

# Linux
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
```

### Option 3: Python-Only (Fallback - WeasyPrint)

```bash
# Install WeasyPrint for HTML-to-PDF conversion
pip install weasyprint

# Windows additional requirements:
# Download GTK3 runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
```

## Python Dependencies

Add to `requirements.txt`:
```
weasyprint>=60.0
```

Install:
```bash
pip install -r requirements.txt
```

## How It Works

1. **Your Resume**: `resume_arnold_sde.tex` contains your actual LaTeX resume
2. **Optimization**: System analyzes JD and adds missing skills to LaTeX
3. **PDF Generation**: Three fallback methods:
   - **pdflatex** (best quality, requires LaTeX)
   - **tectonic** (modern, self-contained)
   - **weasyprint** (Python-only, converts LaTeX→HTML→PDF)

## Testing

### Test PDF Generation:
```bash
cd c:\Users\80133\Maang-Tracker
python -c "from services.latex_pdf_converter import LatexToPdfConverter; c = LatexToPdfConverter(); print(c.generate_resume_pdf(open('resume_arnold_sde.tex').read(), 'test_job'))"
```

### Check Generated PDFs:
```bash
dir resumes\generated
```

## Usage in Dashboard

1. **Analyze Resume** → Click on any job
2. **Create Optimized Resume** → System adds missing skills
3. **Download Resume PDF** → Generates actual PDF file

The button now:
- ✅ Calls `/api/resume/generate-pdf` with LaTeX content
- ✅ Generates PDF with filename: `arnold_gnanaselvam_{job_title}_{timestamp}.pdf`
- ✅ Downloads directly to your computer
- ✅ Falls back to browser print if PDF generation fails

## Verification

Check if PDF was generated:
```bash
# View generated PDFs
ls resumes/generated/

# Or in PowerShell
Get-ChildItem resumes\generated
```

## Troubleshooting

**"pdflatex not found"**
- Install MiKTeX or use Option 2/3

**"WeasyPrint error"**
- Install GTK3 runtime (Windows)
- Check: `pip show weasyprint`

**PDF not downloading**
- Check browser console for errors
- Verify backend is running: `http://localhost:5100`
- Check terminal for PDF generation logs

## Current Status

✅ Your actual LaTeX resume is integrated
✅ PDF generation endpoints are ready
✅ Frontend download button configured
⏳ Waiting for LaTeX compiler installation

**Next Step:** Install one of the options above, then restart the backend!
