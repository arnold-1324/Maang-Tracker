"""
Application Tracking Service
Monitors job applications and verifies submission status
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import json

class ApplicationTracker:
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER", "your-email@gmail.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
    def record_application(self, job_data, resume_path, ats_score):
        """
        Record a job application in the database
        Returns application ID and tracking details
        """
        from memory.db import get_conn
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Insert application record
            cur.execute("""
                INSERT INTO job_applications 
                (user_id, job_id, status, resume_path, ats_score, applied_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (1, job_data['id'], 'Applied', resume_path, ats_score))
            
            app_id = cur.lastrowid
            conn.commit()
            
            # Generate tracking ID
            tracking_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{app_id:04d}"
            
            return {
                "application_id": app_id,
                "tracking_id": tracking_id,
                "applied_at": datetime.now().isoformat(),
                "status": "Applied"
            }
        except Exception as e:
            print(f"Error recording application: {e}")
            return None
        finally:
            conn.close()
    
    def send_confirmation_email(self, user_email, job_data, tracking_id):
        """
        Send application confirmation email
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Application Confirmed: {job_data['role']} at {job_data['company']}"
            msg['From'] = self.email_user
            msg['To'] = user_email
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h2 style="color: #2563eb;">✅ Application Submitted Successfully</h2>
                    
                    <div style="background: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Job Details</h3>
                        <p><strong>Company:</strong> {job_data['company']}</p>
                        <p><strong>Role:</strong> {job_data['role']}</p>
                        <p><strong>Location:</strong> {job_data.get('location', 'Remote')}</p>
                    </div>
                    
                    <div style="background: #dbeafe; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p><strong>Tracking ID:</strong> <code style="background: #fff; padding: 4px 8px; border-radius: 4px;">{tracking_id}</code></p>
                        <p><strong>Applied On:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Status:</strong> <span style="color: #16a34a; font-weight: bold;">Applied</span></p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <h4>Next Steps:</h4>
                        <ol>
                            <li>Check your email for confirmation from {job_data['company']}</li>
                            <li>Monitor your application status in the dashboard</li>
                            <li>Prepare for potential interviews</li>
                        </ol>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        This is an automated confirmation from MAANG Tracker. 
                        Visit your dashboard to track all applications.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email (if credentials are configured)
            if self.email_password:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg)
                return True
            else:
                # Log email content for demo
                print(f"\n{'='*60}")
                print("📧 EMAIL CONFIRMATION (Demo Mode - No SMTP configured)")
                print(f"{'='*60}")
                print(f"To: {user_email}")
                print(f"Subject: {msg['Subject']}")
                print(f"Tracking ID: {tracking_id}")
                print(f"{'='*60}\n")
                return True
                
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def get_application_status(self, tracking_id):
        """
        Get current status of an application by tracking ID
        """
        from memory.db import get_conn
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Extract app_id from tracking_id
            app_id = int(tracking_id.split('-')[-1])
            
            cur.execute("""
                SELECT ja.*, jp.company, jp.title as role, jp.url
                FROM job_applications ja
                JOIN job_postings jp ON ja.job_id = jp.id
                WHERE ja.id = ?
            """, (app_id,))
            
            row = cur.fetchone()
            if row:
                return {
                    "tracking_id": tracking_id,
                    "status": row['status'],
                    "company": row['company'],
                    "role": row['role'],
                    "applied_at": row['applied_at'],
                    "ats_score": row['ats_score'],
                    "url": row['url']
                }
            return None
        finally:
            conn.close()
    
    def get_all_applications(self, user_id=1):
        """
        Get all applications for a user
        """
        from memory.db import get_conn
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT ja.*, jp.company, jp.title as role, jp.location, jp.url
                FROM job_applications ja
                JOIN job_postings jp ON ja.job_id = jp.id
                WHERE ja.user_id = ?
                ORDER BY ja.applied_at DESC
            """, (user_id,))
            
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def update_status(self, tracking_id, new_status, notes=None):
        """
        Update application status (e.g., from email/portal check)
        """
        from memory.db import get_conn
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            app_id = int(tracking_id.split('-')[-1])
            
            cur.execute("""
                UPDATE job_applications 
                SET status = ?
                WHERE id = ?
            """, (new_status, app_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False
        finally:
            conn.close()
