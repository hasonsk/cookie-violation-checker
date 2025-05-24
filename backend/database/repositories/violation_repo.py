from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from . import BaseRepository
from ..connection import MongoDBConnection
from ..schemas import ViolationSchema, CookieViolationReportSchema

logger = logging.getLogger(__name__)

class ViolationRepository(BaseRepository):
    """Repository for violation operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, ViolationSchema.collection_name)

    async def create_violation(self, website_url: str, cookie_name: str, rule_id: int,
                             violation_type: str, feature_type: str,
                             description: str, severity: str = "medium") -> Dict[str, Any]:
        """Create a new violation record"""
        document = ViolationSchema.create_document(
            website_url=website_url,
            cookie_name=cookie_name,
            rule_id=rule_id,
            violation_type=violation_type,
            feature_type=feature_type,
            description=description,
            severity=severity
        )
        return await self.create(document)

    async def create_many_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple violations"""
        documents = []
        for violation in violations:
            doc = ViolationSchema.create_document(**violation)
            documents.append(doc)

        return await self.crud.create_many(documents)

    async def get_violations_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all violations for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url},
            sort=[("severity", 1), ("violation_type", 1), ("cookie_name", 1)]
        )

    async def get_violations_by_cookie(self, website_url: str, cookie_name: str) -> List[Dict[str, Any]]:
        """Get violations for a specific cookie"""
        return await self.get_many(
            filter_dict={"website_url": website_url, "cookie_name": cookie_name},
            sort=[("severity", 1), ("violation_type", 1)]
        )

    async def get_violations_by_type(self, violation_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get violations by type"""
        return await self.get_many(
            filter_dict={"violation_type": violation_type},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_violations_by_severity(self, severity: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get violations by severity"""
        return await self.get_many(
            filter_dict={"severity": severity},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_high_severity_violations(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get high severity violations"""
        return await self.get_violations_by_severity("high", limit)

    async def get_recent_violations(self, hours_ago: int = 24, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent violations within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours_ago)
        return await self.get_many(
            filter_dict={"created_at": {"$gte": time_threshold}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_violation_summary_by_website(self, website_url: str) -> Dict[str, Any]:
        """Get violation summary for a website"""
        pipeline = [
            {"$match": {"website_url": website_url}},
            {
                "$group": {
                    "_id": {
                        "violation_type": "$violation_type",
                        "severity": "$severity"
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        results = await self.crud.aggregate(pipeline)

        summary = {
            "total_violations": len(results),
            "by_type": {},
            "by_severity": {},
            "by_feature_type": {}
        }

        for result in results:
            v_type = result["_id"]["violation_type"]
            severity = result["_id"]["severity"]
            count = result["count"]

            summary["by_type"][v_type] = summary["by_type"].get(v_type, 0) + count
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + count

        # Get feature type breakdown
        feature_pipeline = [
            {"$match": {"website_url": website_url}},
            {"$group": {"_id": "$feature_type", "count": {"$sum": 1}}}
        ]

        feature_results = await self.crud.aggregate(feature_pipeline)
        for result in feature_results:
            summary["by_feature_type"][result["_id"]] = result["count"]

        return summary

    async def delete_violations_by_website(self, website_url: str) -> int:
        """Delete all violations for a website"""
        return await self.crud.delete_many({"website_url": website_url})


class CookieViolationReportRepository(BaseRepository):
    """Repository for cookie violation report operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, CookieViolationReportSchema.collection_name)

    async def create_violation_report(self, website_url: str, cookie_name: str, domain: str,
                                    value_preview: str, declared_info: Dict[str, Any],
                                    actual_info: Dict[str, Any], violations: List[Dict[str, Any]],
                                    feature_type: str) -> Dict[str, Any]:
        """Create a new cookie violation report"""
        document = CookieViolationReportSchema.create_document(
            website_url=website_url,
            cookie_name=cookie_name,
            domain=domain,
            value_preview=value_preview,
            declared_info=declared_info,
            actual_info=actual_info,
            violations=violations,
            feature_type=feature_type
        )
        return await self.create(document)

    async def create_many_reports(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple violation reports"""
        documents = []
        for report in reports:
            doc = CookieViolationReportSchema.create_document(**report)
            documents.append(doc)

        return await self.crud.create_many(documents)

    async def get_reports_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all violation reports for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url},
            sort=[("cookie_name", 1)]
        )

    async def get_report_by_cookie(self, website_url: str, cookie_name: str) -> Optional[Dict[str, Any]]:
        """Get violation report for a specific cookie"""
        return await self.get_by_filter({
            "website_url": website_url,
            "cookie_name": cookie_name
        })

    async def get_reports_by_feature_type(self, feature_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get reports by feature type"""
        return await self.get_many(
            filter_dict={"feature_type": feature_type},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_reports_with_high_severity(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get reports containing high severity violations"""
        return await self.get_many(
            filter_dict={"violations.severity": "high"},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def search_reports_by_cookie_name(self, cookie_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search reports by cookie name"""
        return await self.get_many(
            filter_dict={"cookie_name": {"$regex": cookie_name, "$options": "i"}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_domain_violation_stats(self) -> List[Dict[str, Any]]:
        """Get violation statistics by domain"""
        pipeline = [
            {
                "$group": {
                    "_id": "$domain",
                    "total_reports": {"$sum": 1},
                    "total_violations": {"$sum": {"$size": "$violations"}},
                    "websites": {"$addToSet": "$website_url"}
                }
            },
            {
                "$addFields": {
                    "website_count": {"$size": "$websites"}
                }
            },
            {
                "$project": {
                    "domain": "$_id",
                    "total_reports": 1,
                    "total_violations": 1,
                    "website_count": 1,
                    "_id": 0
                }
            },
            {"$sort": {"total_violations": -1}},
            {"$limit": 20}
        ]

        return await self.crud.aggregate(pipeline)
