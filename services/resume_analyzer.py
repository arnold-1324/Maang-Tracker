import re
import json
from memory.db import get_conn

class Resumeanalyzer:
    def __init__(self):
        # Basic keyword lists (expansible)
        self.tech_keywords = {
            'languages': ['python', 'java', 'c++', 'go', 'golang', 'javascript', 'typescript', 'sql', 'c#'],
            'frameworks': ['react', 'next.js', 'flask', 'django', 'spring', 'dotnet', 'kubernetes', 'docker', 'aws', 'azure'],
            'concepts': ['distributed systems', 'microservices', 'system design', 'rest api', 'graphql', 'ci/cd', 'agile']
        }

    def analyze_resume(self, resume_text, job_description):
        """
        Analyze resume against job description.
        Returns score (0-100), missing skills, matched keywords, and OPTIMIZATION suggestions.
        """
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        # 1. Extract keywords from JD
        jd_keywords = self._extract_skills(jd_lower)
        
        # 2. Check matches in resume
        matches = []
        missing = []
        
        for skill in jd_keywords:
            if skill in resume_lower:
                matches.append(skill)
            else:
                missing.append(skill)
        
        # 3. Calculate Score
        total_skills = len(jd_keywords)
        if total_skills > 0:
            score = (len(matches) / total_skills) * 100
        else:
            score = 65 # Baseline if no specific tech keywords found (generic role)

        # 4. Resume Optimization Logic (Target: 89%+)
        optimization_plan = {}
        modified_resume_snippet = ""
        
        if score < 89:
            # Suggest improvements to boost score
            optimization_plan = {
                "action": "Needs Optimization",
                "missing_critical_skills": missing,
                "strategy": "Integrate missing keywords into 'Skills' and 'Project' sections."
            }
            
            # Generate a "Modified" snippet idea
            if missing:
                modified_resume_snippet = f"Suggested Addition to 'Technical Skills': {', '.join(missing)}"
                
        return {
            "score": round(score, 1),
            "total_keywords": total_skills,
            "matched_keywords": matches,
            "missing_skills": missing,
            "suggestions": self._generate_suggestions(missing),
            "optimization": optimization_plan,
            "modified_resume_snippet": modified_resume_snippet
        }

    def _extract_skills(self, text):
        """
        Enhanced keyword extractor.
        1. Uses predefined tech list.
        2. Scans for 'Qualifications' sections in JD.
        """
        found_skills = set()
        
        # Predefined list check
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                # Word boundary check
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    found_skills.add(keyword)
        
        # Heuristic: Look for capital words near 'Experience with' or 'Proficiency in'
        # (Simplified for this version, rely mostly on list)
        
        return list(found_skills)

    def _generate_suggestions(self, missing_skills):
        if not missing_skills:
            return "ATS Score is high! Your resume covers all detected requirements."
        
        suggestions = "Your resume is missing key requirements found in the JD. "
        suggestions += f"Add these to reach >89%: {', '.join(missing_skills[:5])}"
        return suggestions

    def save_analysis(self, resume_id, job_id, analysis_result):
        """Save ATS analysis to DB"""
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO ats_analysis (resume_id, job_id, score, missing_skills, keyword_matches, suggestions, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                resume_id,
                job_id,
                analysis_result['score'],
                json.dumps(analysis_result['missing_skills']),
                json.dumps(analysis_result['matched_keywords']),
                analysis_result['suggestions']
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def optimize_resume_latex(self, latex_content, missing_skills):
        """
        Injects missing skills into the LaTeX resume content to improve ATS score.
        Target: \section*{Technical Skills} or equivalent.
        """
        if not missing_skills:
            return latex_content
            
        # Strategy: Find "Technical Skills" section and append missing skills to "Languages" or "Core Backend"
        # 1. Look for \section*{Technical Skills}
        # 2. Look for the tabular environment inside it
        # 3. Append to the first row (usually Languages or Core Backend)
        
        optimized_content = latex_content
        
        # Simple injection: Attempt to find "Languages:" line and append there
        # Regex to find: \textbf{Languages:} & ... \\
        
        skills_to_add = ", ".join([s.title() for s in missing_skills])
        
        # Try finding Languages row
        pattern = r"(\\textbf{Languages:}.*?)( \\\\)"
        match = re.search(pattern, optimized_content)
        
        if match:
            # Append skills to Languages row
            existing_line = match.group(1)
            new_line = f"{existing_line}, {skills_to_add}" 
            optimized_content = optimized_content.replace(match.group(0), f"{new_line} \\\\")
        else:
            # Fallback: Find \end{tabular} and add a new row
            fallback_pattern = r"(\\end{tabular})"
            new_row = f"\\\\ \\textbf{{Optimized Additions:}} & {skills_to_add} \\\\"
            optimized_content = re.sub(fallback_pattern, f"{new_row}\n\\1", optimized_content)
            
        return optimized_content
