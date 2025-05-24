from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

class MongoBaseSchema:
    """Base schema for MongoDB documents"""

    @staticmethod
    def to_dict(obj) -> Dict[str, Any]:
        """Convert object to dictionary for MongoDB storage"""
        if hasattr(obj, 'dict'):
            data = obj.dict()
        elif isinstance(obj, dict):
            data = obj
        else:
            data = obj.__dict__

        # Add timestamps if not present
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        return data

    @staticmethod
    def from_dict(data: Dict[str, Any], exclude_id: bool = True) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        if exclude_id and '_id' in data:
            data.pop('_id')
        return data


class TaskSchema(MongoBaseSchema):
    """Schema for task documents"""
    collection_name = "tasks"

    @staticmethod
    def create_document(task_id: str, status: str, message: str, **kwargs) -> Dict[str, Any]:
        return {
            "task_id": task_id,
            "status": status,
            "message": message,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class PolicyDiscoverySchema(MongoBaseSchema):
    """Schema for policy discovery documents"""
    collection_name = "policy_discoveries"

    @staticmethod
    def create_document(website_url: str, policy_url: Optional[str] = None,
                       discovery_method: str = "not_found", error: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "policy_url": policy_url,
            "discovery_method": discovery_method,
            "error": error,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class PolicyContentSchema(MongoBaseSchema):
    """Schema for policy content documents"""
    collection_name = "policy_contents"

    @staticmethod
    def create_document(website_url: str, policy_url: Optional[str] = None,
                       original_content: Optional[str] = None,
                       translated_content: Optional[str] = None,
                       table_content: Optional[List[Dict[str, Any]]] = None,
                       translated_table_content: Optional[str] = None,
                       error: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "policy_url": policy_url,
            "original_content": original_content,
            "translated_content": translated_content,
            "table_content": table_content,
            "translated_table_content": translated_table_content,
            "error": error,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class CookieFeatureSchema(MongoBaseSchema):
    """Schema for cookie feature documents"""
    collection_name = "cookie_features"

    @staticmethod
    def create_document(website_url: str, name: Optional[str] = None,
                       purpose: Optional[str] = None, retention: Optional[str] = None,
                       third_party: Optional[List[str]] = None,
                       behavior: Optional[str] = None,
                       feature_type: str = "undefined", **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "name": name,
            "purpose": purpose,
            "retention": retention,
            "third_party": third_party,
            "behavior": behavior,
            "feature_type": feature_type,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class LiveCookieSchema(MongoBaseSchema):
    """Schema for live cookie documents"""
    collection_name = "live_cookies"

    @staticmethod
    def create_document(website_url: str, name: str, domain: str, path: str,
                       value: str, expires: Optional[float] = None,
                       httpOnly: bool = False, secure: bool = False,
                       sameSite: Optional[str] = None, session: bool = False,
                       **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "name": name,
            "domain": domain,
            "path": path,
            "value": value,
            "expires": expires,
            "httpOnly": httpOnly,
            "secure": secure,
            "sameSite": sameSite,
            "session": session,
            "collected_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class ViolationSchema(MongoBaseSchema):
    """Schema for violation documents"""
    collection_name = "violations"

    @staticmethod
    def create_document(website_url: str, cookie_name: str, rule_id: int,
                       violation_type: str, feature_type: str,
                       description: str, severity: str = "medium",
                       **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "cookie_name": cookie_name,
            "rule_id": rule_id,
            "violation_type": violation_type,
            "feature_type": feature_type,
            "description": description,
            "severity": severity,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class CookieViolationReportSchema(MongoBaseSchema):
    """Schema for cookie violation report documents"""
    collection_name = "cookie_violation_reports"

    @staticmethod
    def create_document(website_url: str, cookie_name: str, domain: str,
                       value_preview: str, declared_info: Dict[str, Any],
                       actual_info: Dict[str, Any], violations: List[Dict[str, Any]],
                       feature_type: str, **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "cookie_name": cookie_name,
            "domain": domain,
            "value_preview": value_preview,
            "declared_info": declared_info,
            "actual_info": actual_info,
            "violations": violations,
            "feature_type": feature_type,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


class WebsiteReportSchema(MongoBaseSchema):
    """Schema for website report documents"""
    collection_name = "website_reports"

    @staticmethod
    def create_document(website_url: str, scan_time: datetime,
                       policy_found: bool, policy_url: Optional[str] = None,
                       total_cookies: int = 0, violating_cookies: int = 0,
                       violations_by_type: Dict[str, int] = None,
                       violations_by_feature: Dict[str, int] = None,
                       cookie_violations: List[Dict[str, Any]] = None,
                       summary: str = "", **kwargs) -> Dict[str, Any]:
        return {
            "website_url": website_url,
            "scan_time": scan_time,
            "policy_found": policy_found,
            "policy_url": policy_url,
            "total_cookies": total_cookies,
            "violating_cookies": violating_cookies,
            "violations_by_type": violations_by_type or {},
            "violations_by_feature": violations_by_feature or {},
            "cookie_violations": cookie_violations or [],
            "summary": summary,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }


# Collection mapping for easy access
COLLECTION_SCHEMAS = {
    "tasks": TaskSchema,
    "policy_discoveries": PolicyDiscoverySchema,
    "policy_contents": PolicyContentSchema,
    "cookie_features": CookieFeatureSchema,
    "live_cookies": LiveCookieSchema,
    "violations": ViolationSchema,
    "cookie_violation_reports": CookieViolationReportSchema,
    "website_reports": WebsiteReportSchema,
}
