import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base


class MergeHistory(Base):
    __tablename__ = "merge_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    output_filename = Column(String(255), nullable=False)
    original_filenames = Column(Text, nullable=False)  # JSON array
    file_count = Column(Integer, nullable=False)
    total_pages = Column(Integer, default=0)
    output_size_bytes = Column(BigInteger, default=0)
    page_ranges = Column(Text, nullable=True)  # JSON
    watermark_applied = Column(String(255), nullable=True)
    compressed = Column(Integer, default=0)  # 0=no, 1=yes
    download_token = Column(String(255), unique=True, nullable=True)
    download_expires_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)
    status = Column(String(20), default="completed")  # completed, expired, deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="merge_histories")

    def __repr__(self):
        return f"<MergeHistory {self.output_filename}>"