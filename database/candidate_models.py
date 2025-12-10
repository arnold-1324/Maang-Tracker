
# ============= JOB APPLICATION TRACKER =============
class JobPosting(Base):
    """Job postings crawled or added manually"""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    url = Column(String(512), unique=True)
    description = Column(Text) # Full JD
    source = Column(String(50)) # LinkedIn, Indeed, etc.
    posted_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_job_company', 'company'),
        Index('idx_job_url', 'url'),
    )

class JobApplication(Base):
    """User's applications to jobs"""
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(Integer, ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(String(50), default='Saved') # Saved, Applied, Interviewing, Offer, Rejected
    
    # Resume versions
    original_resume_path = Column(String(512))
    optimized_resume_path = Column(String(512))
    
    # Scores
    original_ats_score = Column(Float, default=0.0)
    optimized_ats_score = Column(Float, default=0.0)
    
    # Cover Letter
    cover_letter_path = Column(String(512))
    
    # Tracking
    applied_date = Column(DateTime)
    last_status_check = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User")
    job = relationship("JobPosting", back_populates="applications")

    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='unique_application'),
        Index('idx_app_status', 'status'),
    )
