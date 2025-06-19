from datetime import datetime

class ProcessedMatch:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.processed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage"""
        return {
            "match_id": self.match_id,
            "processed_at": self.processed_at.isoformat() + "Z"
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessedMatch':
        """Create ProcessedMatch from MongoDB document, handling both camelCase and snake_case"""
        # Handle both camelCase (matchId) and snake_case (match_id) for backward compatibility
        match_id = data.get("match_id") or data.get("matchId")
        if not match_id:
            raise ValueError("ProcessedMatch document must have match_id or matchId field")
        
        processed_match = cls(match_id)
        
        # Handle both camelCase (processedAt) and snake_case (processed_at) for datetime
        processed_at_str = data.get("processed_at") or data.get("processedAt")
        if processed_at_str:
            try:
                if isinstance(processed_at_str, str):
                    # Handle ISO string format
                    processed_match.processed_at = datetime.fromisoformat(processed_at_str.replace("Z", "+00:00"))
                elif hasattr(processed_at_str, 'replace'):
                    # Handle MongoDB datetime objects
                    processed_match.processed_at = processed_at_str.replace(tzinfo=None)
                else:
                    # Fallback to current time
                    processed_match.processed_at = datetime.utcnow()
            except Exception as e:
                print(f"Warning: Could not parse processed_at date: {e}")
                processed_match.processed_at = datetime.utcnow()
        
        return processed_match 