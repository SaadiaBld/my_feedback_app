from pydantic import BaseModel

class DashboardKPIs(BaseModel):
    current_reviews: int
    previous_reviews: int
    delta_reviews: int
    current_avg_rating: float
    previous_avg_rating: float
    delta_avg_rating: float

class TopThemes(BaseModel):
    top_satisfaction: str
    top_satisfaction_score: float
    top_irritant: str
    top_irritant_score: float

class WeeklySatisfactionPoint(BaseModel):
    week: str
    avg_score: float

class ThemeDistribution(BaseModel):
    theme: str
    count: int