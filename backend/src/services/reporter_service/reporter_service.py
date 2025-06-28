from typing import Dict, Any
from datetime import datetime, timedelta
from backend.src.repositories.website_repository import WebsiteRepository
from backend.src.repositories.violation_repository import ViolationRepository
from backend.src.models.website import Website
from backend.src.models.violation import Violation
from pymongo.database import Database

class ReporterService:
    def __init__(self, db: Database):
        self.website_repository = WebsiteRepository(db)
        self.violation_repository = ViolationRepository(db)

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        total_websites = await self.website_repository.count_documents({})
        total_violations = await self.violation_repository.count_documents({})

        # Example: Get violations in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_violations_count = await self.violation_repository.count_documents(
            {"timestamp": {"$gte": thirty_days_ago}}
        )

        # Example: Violations by type (assuming 'type' field in Violation model)
        violation_types_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        violations_by_type = await self.violation_repository.aggregate(violation_types_pipeline)

        # Example: Websites by status (assuming 'status' field in Website model)
        website_status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        websites_by_status = await self.website_repository.aggregate(website_status_pipeline)

        return {
            "total_websites": total_websites,
            "total_violations": total_violations,
            "recent_violations_count": recent_violations_count,
            "violations_by_type": list(violations_by_type),
            "websites_by_status": list(websites_by_status),
            # Add more metrics as needed
        }

    async def get_violations_over_time(self, days: int = 30) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]
        violations_data = await self.violation_repository.aggregate(pipeline)

        # Format data for frontend charting
        formatted_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            count = 0
            for item in violations_data:
                item_date = datetime(item["_id"]["year"], item["_id"]["month"], item["_id"]["day"])
                if item_date.strftime("%Y-%m-%d") == date_str:
                    count = item["count"]
                    break
            formatted_data.append({"date": date_str, "count": count})
            current_date += timedelta(days=1)

        return {"violations_over_time": formatted_data}
