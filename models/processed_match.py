from datetime import datetime

class ProcessedMatch:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.processed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "processed_at": self.processed_at.isoformat() + "Z"
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessedMatch':
        processed_match = cls(data["match_id"])
        
        # Parse datetime string
        if "processed_at" in data:
            try:
                processed_match.processed_at = datetime.fromisoformat(data["processed_at"].replace("Z", "+00:00"))
            except:
                processed_match.processed_at = datetime.utcnow()
                
        return processed_match 