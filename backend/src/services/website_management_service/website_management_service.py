from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from loguru import logger

from src.repositories.website_repository import WebsiteRepository
from src.repositories.violation_repository import ViolationRepository
from src.schemas.website import WebsiteListResponseSchema, WebsiteCreateSchema, WebsiteUpdateSchema, WebsiteResponseSchema
from src.models.website import Website
from src.models.user import UserRole # Import UserRole
from src.exceptions.custom_exceptions import NotFoundException, BadRequestException # Import custom exceptions

class WebsiteManagementService:
    def __init__(self, website_repo: WebsiteRepository, violation_repo: ViolationRepository):
        self.website_repo = website_repo
        self.violation_repo = violation_repo

    async def get_all_websites(self, user_id: str, user_role: UserRole, search_query: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[WebsiteListResponseSchema]:
        filters = {}
        if search_query:
            filters["domain"] = {"$regex": search_query, "$options": "i"} # Case-insensitive search

        # Filter by provider_id if the user is a provider
        if user_role == UserRole.PROVIDER:
            filters["provider_id"] = ObjectId(user_id)

        websites_data = await self.website_repo.get_all_websites(filters, skip=skip, limit=limit)

        response_list = []
        for website_data in websites_data:
            website = Website.model_validate(website_data) # Use model_validate

            # Calculate check_count and last_checked_at (assuming 'violations' collection stores check history)
            # This is a simplified approach. A more robust solution might involve a dedicated 'checks' collection
            # or more complex aggregation queries.
            violations = await self.violation_repo.get_violations_by_website(str(website.domain))
            # logger.debug(f"Found {(violations)} violations for website {website.domain}")
            check_count = len(violations) # Count unique check dates

            # last_checked_at = None
            # if violations:
            #     last_checked_at = max([v.checked_at for v in violations])

            # Calculate policy_status (simplified, needs actual logic based on compliance analysis)
            policy_status = "unknown"
            if website.is_specific is not None:
                policy_status = "specific" if website.is_specific == 1 else "general"

            # Calculate num_specified_cookies
            num_specified_cookies = len(website.policy_cookies)

            # logger.warning(f"Website {website.domain} has {violations}.")
            # Calculate average violations
            # total_violations = sum([len(v.issues) for v in violations])
            # avg_violations = total_violations / check_count if check_count > 0 else 0.0

            response_list.append(
                WebsiteListResponseSchema(
                    id=website.id, # Pass PyObjectId directly
                    domain=str(website.domain),
                    company_name=website.company_name,
                    check_count=check_count,
                    policy_status=policy_status,
                    policy_url=website.policy_url,
                    num_specified_cookies=num_specified_cookies,
                    # avg_violations=avg_violations,
                    # last_checked_at=last_checked_at
                )
            )
        return response_list

    async def get_website_by_id(self, website_id: str) -> WebsiteResponseSchema:
        website_data = await self.website_repo.get_by_id(website_id)
        if not website_data:
            raise NotFoundException(f"Website with ID {website_id} not found")
        return WebsiteResponseSchema.model_validate(website_data)

    async def create_website(self, website_data: WebsiteCreateSchema, user_id: str) -> WebsiteResponseSchema:
        # Check if a website with the same domain already exists for this provider
        existing_website = await self.website_repo.get_by_domain_and_provider(website_data.domain, user_id)
        if existing_website:
            raise BadRequestException(f"Website with domain '{website_data.domain}' already exists for this provider.")

        website_dict = website_data.model_dump()
        website_dict["provider_id"] = ObjectId(user_id) # Assign the current user as the provider
        website_dict["created_at"] = datetime.utcnow()
        website_dict["updated_at"] = datetime.utcnow()

        new_website_id = await self.website_repo.create(website_dict)
        created_website = await self.website_repo.get_by_id(new_website_id)
        return WebsiteResponseSchema.model_validate(created_website)

    async def update_website(self, website_id: str, website_data: WebsiteUpdateSchema) -> WebsiteResponseSchema:
        website_dict = website_data.model_dump(exclude_unset=True)
        website_dict["updated_at"] = datetime.utcnow()

        updated_count = await self.website_repo.update(website_id, website_dict)
        if updated_count == 0:
            raise NotFoundException(f"Website with ID {website_id} not found")

        updated_website = await self.website_repo.get_by_id(website_id)
        return WebsiteResponseSchema.model_validate(updated_website)

    async def delete_website(self, website_id: str):
        deleted_count = await self.website_repo.delete(website_id)
        if deleted_count == 0:
            raise NotFoundException(f"Website with ID {website_id} not found")

    async def get_website_analytics(self, website_id: str) -> dict:
        """
        Retrieves analytics data for a specific website.
        This is a placeholder implementation.
        """
        # Example: Fetch website details and some violation summary
        website = await self.website_repo.get_by_id(website_id)
        if not website:
            raise NotFoundException(f"Website with ID {website_id} not found")

        violations = await self.violation_repo.get_violations_by_website_id(website_id)

        # Basic analytics: total violations, last check date, etc.
        total_violations_count = sum(len(v.violations) for v in violations)
        # last_checked_at = max([v.checked_at for v in violations]) if violations else None

        return {
            "website_id": website_id,
            "domain": str(website.domain),
            "total_violations_found": total_violations_count,
            "number_of_checks": len(violations),
            # "last_checked_at": last_checked_at.isoformat() if last_checked_at else None,
            "analytics_data_placeholder": "More detailed analytics would go here."
        }

    async def trigger_website_analysis(self, payload: dict) -> dict:
        """
        Triggers the analysis process for a website.
        This is a placeholder implementation.
        """
        # In a real application, this would likely involve:
        # 1. Validating the payload (e.g., website_id or domain)
        # 2. Enqueuing a task to a background worker (e.g., Celery, Redis Queue)
        # 3. Returning a task ID or confirmation

        # For now, just acknowledge the request
        website_id = payload.get("website_id")
        domain = payload.get("domain")

        if not website_id and not domain:
            raise BadRequestException("Either 'website_id' or 'domain' must be provided in the payload.")

        print(f"Initiating analysis for website_id: {website_id}, domain: {domain}")
        # Simulate some work
        import asyncio
        await asyncio.sleep(1)

        return {"status": "Analysis initiated", "website_id": website_id, "domain": domain}
