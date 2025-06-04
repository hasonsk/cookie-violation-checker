from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from . import BaseRepository
from ..connection import MongoDBConnection
from ..schemas import CookieFeatureSchema, LiveCookieSchema

class CookieFeatureRepository(BaseRepository):
    """Repository for cookie feature operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, CookieFeatureSchema.collection_name)

    async def create_cookie_feature(self, website_url: str, name: Optional[str] = None,
                                  purpose: Optional[str] = None, retention: Optional[str] = None,
                                  third_party: Optional[List[str]] = None,
                                  behavior: Optional[str] = None,
                                  feature_type: str = "undefined") -> Dict[str, Any]:
        """Create a new cookie feature record"""
        document = CookieFeatureSchema.create_document(
            website_url=website_url,
            name=name,
            purpose=purpose,
            retention=retention,
            third_party=third_party,
            behavior=behavior,
            feature_type=feature_type
        )
        return await self.create(document)

    async def get_features_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all cookie features for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url},
            sort=[("feature_type", 1), ("name", 1)]
        )

    async def get_specific_features(self, website_url: str) -> List[Dict[str, Any]]:
        """Get specific cookie features for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url, "feature_type": "specific"},
            sort=[("name", 1)]
        )

    async def get_general_features(self, website_url: str) -> List[Dict[str, Any]]:
        """Get general cookie features for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url, "feature_type": "general"},
            sort=[("purpose", 1)]
        )

    async def get_feature_by_name(self, website_url: str, cookie_name: str) -> Optional[Dict[str, Any]]:
        """Get specific cookie feature by name"""
        return await self.get_by_filter({
            "website_url": website_url,
            "name": cookie_name,
            "feature_type": "specific"
        })

    async def get_features_by_type(self, feature_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get features by type"""
        return await self.get_many(
            filter_dict={"feature_type": feature_type},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def update_feature(self, website_url: str, name: str, **update_fields) -> Optional[Dict[str, Any]]:
        """Update a cookie feature"""
        return await self.update(
            {"website_url": website_url, "name": name},
            update_fields
        )

    async def delete_features_by_website(self, website_url: str) -> int:
        """Delete all features for a website"""
        return await self.crud.delete_many({"website_url": website_url})


class LiveCookieRepository(BaseRepository):
    """Repository for live cookie operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, LiveCookieSchema.collection_name)

    async def create_live_cookie(self, website_url: str, name: str, domain: str, path: str,
                               value: str, expires: Optional[float] = None,
                               httpOnly: bool = False, secure: bool = False,
                               sameSite: Optional[str] = None, session: bool = False) -> Dict[str, Any]:
        """Create a new live cookie record"""
        document = LiveCookieSchema.create_document(
            website_url=website_url,
            name=name,
            domain=domain,
            path=path,
            value=value,
            expires=expires,
            httpOnly=httpOnly,
            secure=secure,
            sameSite=sameSite,
            session=session
        )
        return await self.create(document)

    async def create_many_cookies(self, website_url: str,
                                cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple live cookies for a website"""
        documents = []
        for cookie in cookies:
            doc = LiveCookieSchema.create_document(
                website_url=website_url,
                **cookie
            )
            documents.append(doc)

        return await self.crud.create_many(documents)

    async def get_cookies_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all cookies for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url},
            sort=[("name", 1)]
        )

    async def get_latest_cookies_by_website(self, website_url: str,
                                          hours_ago: int = 24) -> List[Dict[str, Any]]:
        """Get latest cookies for a website within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours_ago)
        return await self.get_many(
            filter_dict={
                "website_url": website_url,
                "collected_at": {"$gte": time_threshold}
            },
            sort=[("collected_at", -1)]
        )

    async def get_cookie_by_name(self, website_url: str, cookie_name: str) -> Optional[Dict[str, Any]]:
        """Get latest cookie by name for a website"""
        results = await self.get_many(
            filter_dict={"website_url": website_url, "name": cookie_name},
            limit=1,
            sort=[("collected_at", -1)]
        )
        return results[0] if results else None

    async def get_session_cookies(self, website_url: str) -> List[Dict[str, Any]]:
        """Get session cookies for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url, "session": True},
            sort=[("name", 1)]
        )

    async def get_persistent_cookies(self, website_url: str) -> List[Dict[str, Any]]:
        """Get persistent cookies for a website"""
        return await self.get_many(
            filter_dict={"website_url": website_url, "session": False},
            sort=[("name", 1)]
        )

    async def get_third_party_cookies(self, website_url: str) -> List[Dict[str, Any]]:
        """Get third-party cookies (different domain) for a website"""
        from urllib.parse import urlparse

        # Extract main domain from website URL
        parsed_url = urlparse(website_url)
        main_domain = parsed_url.netloc.replace('www.', '')

        return await self.get_many(
            filter_dict={
                "website_url": website_url,
                "domain": {"$not": {"$regex": main_domain.replace('.', r'\.')}}
            },
            sort=[("domain", 1), ("name", 1)]
        )

    async def get_expired_cookies(self, website_url: str) -> List[Dict[str, Any]]:
        """Get expired cookies for a website"""
        current_time = datetime.utcnow().timestamp()
        return await self.get_many(
            filter_dict={
                "website_url": website_url,
                "expires": {"$lt": current_time, "$ne": None}
            },
            sort=[("expires", 1)]
        )

    async def delete_cookies_by_website(self, website_url: str) -> int:
        """Delete all cookies for a website"""
        return await self.crud.delete_many({"website_url": website_url})

    async def delete_old_cookies(self, days_old: int = 30) -> int:
        """Delete cookies older than specified days"""
        time_threshold = datetime.utcnow() - timedelta(days=days_old)
        return await self.crud.delete_many({
            "collected_at": {"$lt": time_threshold}
        })

    async def get_cookie_stats(self, website_url: str = None) -> Dict[str, Any]:
        """Get cookie statistics"""
        filter_dict = {"website_url": website_url} if website_url else {}

        total_cookies = await self.count(filter_dict)
        session_cookies = await self.count({**filter_dict, "session": True})
        persistent_cookies = await self.count({**filter_dict, "session": False})
        secure_cookies = await self.count({**filter_dict, "secure": True})
        httponly_cookies = await self.count({**filter_dict, "httpOnly": True})

        # Get domain distribution
        pipeline = [
            {"$match": filter_dict},
            {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]

        domain_stats = await self.crud.aggregate(pipeline)

        return {
            "total_cookies": total_cookies,
            "session_cookies": session_cookies,
            "persistent_cookies": persistent_cookies,
            "secure_cookies": secure_cookies,
            "httponly_cookies": httponly_cookies,
            "top_domains": [{"domain": stat["_id"], "count": stat["count"]} for stat in domain_stats]
        }
