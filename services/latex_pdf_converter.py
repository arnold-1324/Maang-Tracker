"""
LaTeX to PDF Converter Service
Compiles LaTeX files to professional PDF resumes
"""
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class LatexToPdfConverter:
    def __init__(self):
        self.output_dir = Path("resumes/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def compile_latex_to_pdf(self, latex_content, output_filename="resume.pdf"):
        """
        Compile LaTeX content to PDF using pdflatex
        Returns path to generated PDF or None if compilation fails
        """
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Write LaTeX content to temp file
            tex_file = tmpdir_path / "resume.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # Run pdflatex twice for proper formatting (handles references)
                for _ in range(2):
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(tmpdir_path), str(tex_file)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        print(f"LaTeX compilation error:\n{result.stdout}\n{result.stderr}")
                        # Fall back to alternative method
                        return self._compile_with_tectonic(latex_content, output_filename)
                
                # Move generated PDF to output directory
                pdf_file = tmpdir_path / "resume.pdf"
                if pdf_file.exists():
                    output_path = self.output_dir / output_filename
                    shutil.copy(pdf_file, output_path)
                    return str(output_path)
                else:
                    print("PDF file not generated")
                    return None
                    
            except FileNotFoundError:
                print("pdflatex not found. Trying alternative method...")
                return self._compile_with_tectonic(latex_content, output_filename)
            except subprocess.TimeoutExpired:
                print("LaTeX compilation timed out")
                return None
            except Exception as e:
                print(f"Compilation error: {e}")
                return None
    
    def _compile_with_tectonic(self, latex_content, output_filename):
        """
        Alternative: Use Tectonic (modern LaTeX compiler)
        Falls back to online service if local compilation unavailable
        """
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                tex_file = tmpdir_path / "resume.tex"
                
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                result = subprocess.run(
                    ['tectonic', str(tex_file)],
                    capture_output=True,
                    text=True,
                    cwd=tmpdir_path,
                    timeout=30
                )
                
                if result.returncode == 0:
                    pdf_file = tmpdir_path / "resume.pdf"
                    if pdf_file.exists():
                        output_path = self.output_dir / output_filename
                        shutil.copy(pdf_file, output_path)
                        return str(output_path)
                        
        except FileNotFoundError:
            print("Tectonic not found. Using fallback HTML-to-PDF method...")
            return self._compile_with_weasyprint(latex_content, output_filename)
        except Exception as e:
            print(f"Tectonic compilation error: {e}")
            return None
    
    def _compile_with_weasyprint(self, latex_content, output_filename):
        """
        Fallback: Convert LaTeX to HTML then to PDF using WeasyPrint
        Produces clean, professional resume matching Arnold_SDE_strip.pdf style
        """
        try:
            from weasyprint import HTML, CSS
            
            # Enhanced LaTeX to HTML conversion
            html_content = self._latex_to_professional_html(latex_content)
            
            # Professional resume styling matching the original PDF
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    @page {{
                        size: letter;
                        margin: 0.5in 0.6in;
                    }}
                    body {{
                        font-family: 'Times New Roman', Times, serif;
                        font-size: 10.5pt;
                        line-height: 1.3;
                        color: #000;
                        margin: 0;
                        padding: 0;
                    }}
                    
                    /* Header */
                    .header {{
                        text-align: center;
                        margin-bottom: 12pt;
                    }}
                    .header h1 {{
                        font-size: 22pt;
                        font-weight: bold;
                        margin: 0 0 3pt 0;
                        text-transform: uppercase;
                        letter-spacing: 0.5pt;
                    }}
                    .header .subtitle {{
                        font-size: 10pt;
                        font-style: italic;
                        margin: 3pt 0 6pt 0;
                    }}
                    .header .contact {{
                        font-size: 9.5pt;
                        line-height: 1.4;
                    }}
                    
                    /* Sections */
                    h2 {{
                        font-size: 11.5pt;
                        font-weight: bold;
                        text-transform: uppercase;
                        border-bottom: 1.5pt solid #000;
                        margin: 10pt 0 6pt 0;
                        padding-bottom: 2pt;
                        letter-spacing: 0.3pt;
                    }}
                    
                    /* Experience/Education entries */
                    .entry {{
                        margin-bottom: 8pt;
                    }}
                    .entry-header {{
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 1pt;
                    }}
                    .entry-title {{
                        font-weight: bold;
                        font-size: 10.5pt;
                    }}
                    .entry-date {{
                        font-weight: bold;
                        font-size: 9.5pt;
                    }}
                    .entry-subtitle {{
                        font-style: italic;
                        font-size: 10pt;
                        margin-bottom: 3pt;
                    }}
                    
                    /* Lists */
                    ul {{
                        margin: 3pt 0 0 0;
                        padding-left: 18pt;
                        list-style-type: disc;
                    }}
                    li {{
                        margin-bottom: 2pt;
                        font-size: 10pt;
                        line-height: 1.3;
                    }}
                    
                    /* Skills section */
                    .skills-list {{
                        margin: 4pt 0;
                        padding-left: 0;
                        list-style: none;
                    }}
                    .skills-list li {{
                        margin-bottom: 3pt;
                        line-height: 1.4;
                    }}
                    .skill-category {{
                        font-weight: bold;
                    }}
                    
                    /* Summary */
                    .summary {{
                        font-size: 10pt;
                        line-height: 1.35;
                        margin: 4pt 0 8pt 0;
                        text-align: justify;
                    }}
                    
                    /* Links */
                    a {{
                        color: #000;
                        text-decoration: none;
                    }}
                    
                    /* Spacing adjustments */
                    .section {{
                        margin-bottom: 10pt;
                    }}
                    
                    strong {{
                        font-weight: 600;
                    }}
                    
                    em {{
                        font-style: italic;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            output_path = self.output_dir / output_filename
            HTML(string=full_html).write_pdf(output_path)
            return str(output_path)
            
        except ImportError:
            print("WeasyPrint not installed. Install with: pip install weasyprint")
            return None
        except Exception as e:
            print(f"WeasyPrint error: {e}")
            return None
    
    def _latex_to_professional_html(self, latex):
        """Convert LaTeX to clean, professional HTML matching resume style"""
        import re
        
        # Remove preamble
        content = re.sub(r'\\documentclass.*?\\begin\{document\}', '', latex, flags=re.DOTALL)
        content = content.replace('\\end{document}', '')
        
        # Extract header information
        name_match = re.search(r'\\Huge.*?\\scshape\s+(.*?)\}', content)
        name = name_match.group(1) if name_match else "Arnold Gnanaselvam"
        
        # Build HTML structure
        html = '<div class="resume">'
        
        # Header
        html += f'''
        <div class="header">
            <h1>{name}</h1>
            <div class="subtitle">Software Engineer, Product</div>
            <div class="contact">
                Cuddalore, Tamil Nadu, India | +91 9361097319 | arnoldgna765@gmail.com<br>
                github.com/arnold-1324 | linkedin.com/in/arnold-gnanaselvam
            </div>
        </div>
        '''
        
        # Process sections
        sections = re.split(r'\\section\{(.*?)\}', content)[1:]  # Skip before first section
        
        for i in range(0, len(sections), 2):
            if i+1 >= len(sections):
                break
                
            section_title = sections[i]
            section_content = sections[i+1]
            
            html += f'<div class="section"><h2>{section_title}</h2>'
            
            if section_title == "Summary" or section_title == "Learning & Interests":
                # Plain text sections
                text = re.sub(r'\\small\{(.*?)\}', r'\1', section_content, flags=re.DOTALL)
                text = self._clean_latex(text)
                html += f'<div class="summary">{text}</div>'
                
            elif section_title == "Technical Skills":
                # Skills section
                html += '<ul class="skills-list">'
                skills = re.findall(r'\\textbf\{(.*?)\}\{:\s*(.*?)\}', section_content)
                for skill_cat, skill_list in skills:
                    clean_list = self._clean_latex(skill_list)
                    html += f'<li><span class="skill-category">{skill_cat}:</span> {clean_list}</li>'
                html += '</ul>'
                
            else:
                # Experience, Education, Projects, Achievements
                entries = re.findall(r'\\resumeSubheading\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}(.*?)(?=\\resumeSubheading|\\resumeProjectHeading|\\resumeSubHeadingListEnd)', 
                                    section_content, re.DOTALL)
                
                for title, location, subtitle, date, items in entries:
                    html += '<div class="entry">'
                    html += f'''
                    <div class="entry-header">
                        <span class="entry-title">{self._clean_latex(title)}</span>
                        <span class="entry-date">{self._clean_latex(date)}</span>
                    </div>
                    <div class="entry-subtitle">{self._clean_latex(subtitle)} | {self._clean_latex(location)}</div>
                    '''
                    
                    # Extract bullet points
                    bullets = re.findall(r'\\resumeItem\{(.*?)\}', items, re.DOTALL)
                    if bullets:
                        html += '<ul>'
                        for bullet in bullets:
                            clean_bullet = self._clean_latex(bullet)
                            html += f'<li>{clean_bullet}</li>'
                        html += '</ul>'
                    
                    html += '</div>'
                
                # Handle project headings
                projects = re.findall(r'\\resumeProjectHeading\{(.*?)\}\{(.*?)\}(.*?)(?=\\resumeProjectHeading|\\resumeSubHeadingListEnd)', 
                                     section_content, re.DOTALL)
                
                for title, date, items in projects:
                    html += '<div class="entry">'
                    html += f'''
                    <div class="entry-header">
                        <span class="entry-title">{self._clean_latex(title)}</span>
                        <span class="entry-date">{self._clean_latex(date)}</span>
                    </div>
                    '''
                    
                    bullets = re.findall(r'\\resumeItem\{(.*?)\}', items, re.DOTALL)
                    if bullets:
                        html += '<ul>'
                        for bullet in bullets:
                            clean_bullet = self._clean_latex(bullet)
                            html += f'<li>{clean_bullet}</li>'
                        html += '</ul>'
                    
                    html += '</div>'
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _clean_latex(self, text):
        """Remove LaTeX commands and clean text"""
        import re
        
        # Handle common LaTeX commands
        text = re.sub(r'\\textbf\{(.*?)\}', r'<strong>\1</strong>', text)
        text = re.sub(r'\\textit\{(.*?)\}', r'<em>\1</em>', text)
        text = re.sub(r'\\emph\{(.*?)\}', r'<em>\1</em>', text)
        text = re.sub(r'\\href\{(.*?)\}\{(.*?)\}', r'<a href="\1">\2</a>', text)
        
        # Remove other LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?\{.*?\}', '', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        
        # Clean up special characters
        text = text.replace('$|$', '|')
        text = text.replace('$', '')
        text = text.replace('~', ' ')
        text = text.replace('--', '–')
        text = text.replace('\\_', '_')
        text = text.replace('\\&', '&')
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _latex_to_html(self, latex):
        """Convert LaTeX to clean HTML"""
        import re
        html = latex
        
        # Remove preamble
        html = re.sub(r'\\documentclass.*?\\begin\{document\}', '', html, flags=re.DOTALL)
        html = html.replace('\\end{document}', '')
        
        # Headers
        html = re.sub(r'\\textbf\{\\Huge \\scshape (.*?)\}', r'<h1>\1</h1>', html)
        html = re.sub(r'\\section\{(.*?)\}', r'<h2>\1</h2>', html)
        html = re.sub(r'\\textbf\{(.*?)\}', r'<strong>\1</strong>', html)
        html = re.sub(r'\\textit\{(.*?)\}', r'<em>\1</em>', html)
        html = re.sub(r'\\href\{(.*?)\}\{(.*?)\}', r'<a href="\1">\2</a>', html)
        
        # Lists
        html = re.sub(r'\\resumeItemListStart', '<ul>', html)
        html = re.sub(r'\\resumeItemListEnd', '</ul>', html)
        html = re.sub(r'\\resumeItem\{(.*?)\}', r'<li>\1</li>', html, flags=re.DOTALL)
        
        # Clean up LaTeX commands
        html = re.sub(r'\\[a-zA-Z]+(\[.*?\])?\{.*?\}', '', html)
        html = re.sub(r'\\[a-zA-Z]+', '', html)
        html = re.sub(r'\$\|?\$', '|', html)
        
        return html
    
    def generate_resume_pdf(self, latex_content, job_title="", timestamp=None):
        """
        Generate PDF with descriptive filename
        """
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        job_slug = job_title.lower().replace(' ', '_')[:30] if job_title else "resume"
        filename = f"arnold_gnanaselvam_{job_slug}_{timestamp}.pdf"
        
        return self.compile_latex_to_pdf(latex_content, filename)
