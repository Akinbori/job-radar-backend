class OpportunityRecord(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    date_found: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    posted_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    remote_status: Mapped[str] = mapped_column(String(255), nullable=False)

    salary_min_usd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_usd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_confidence: Mapped[str] = mapped_column(String(32), nullable=False)

    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)

    # ✅ ADD THIS
    source_category: Mapped[str] = mapped_column(String(32), nullable=False, default="lead")

    signal_type: Mapped[str] = mapped_column(String(64), nullable=False)

    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    application_url: Mapped[str] = mapped_column(Text, nullable=False)

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    match_reason: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility_risk: Mapped[str] = mapped_column(String(128), nullable=False)

    apply_priority: Mapped[str] = mapped_column(String(32), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(32), nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
