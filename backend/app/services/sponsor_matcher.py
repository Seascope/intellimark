import random
from typing import List
from app.models.sponsor import Sponsor
from app.schemas.sponsor import SponsorMatchRequest, SponsorMatchResponse
from sqlalchemy.orm import Session

class SponsorMatcher:
    def __init__(self, db: Session):
        self.db = db

    def match_sponsors(self, request: SponsorMatchRequest) -> List[SponsorMatchResponse]:
        sponsors = self.db.query(Sponsor).all()

        matches = []
        for sponsor in sponsors:
            score = round(random.uniform(0.4, 0.98), 2)  # simulate AI ranking
            matches.append(
                SponsorMatchResponse(
                    sponsor_id=sponsor.id,
                    sponsor_name=sponsor.name,
                    relevance_score=score
                )
            )

        # Sort by highest score
        return sorted(matches, key=lambda x: x.relevance_score, reverse=True)
