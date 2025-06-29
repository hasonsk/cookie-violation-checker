import pytest
from unittest.mock import AsyncMock, MagicMock
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from unittest.mock import patch

from src.services.domain_request_service import DomainRequestService
from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus
from src.models.domain_request import DomainRequest
from src.exceptions.custom_exceptions import DomainRequestNotFoundError, DomainAlreadyExistsError

@pytest.fixture
def mock_domain_request_repo():
    return AsyncMock()

@pytest.fixture
def mock_website_repo():
    return AsyncMock()

@pytest.fixture
def domain_request_service(mock_domain_request_repo, mock_website_repo):
    return DomainRequestService(mock_domain_request_repo, mock_website_repo)

@pytest.fixture
def sample_requester_id():
    return str(ObjectId())

@pytest.fixture
def sample_domain_request_data():
    return DomainRequestCreateSchema(
        company_name="Test Company",
        domains=["example.com", "test.org"],
        purpose="Testing service"
    )

@pytest.fixture
def sample_domain_request_model(sample_requester_id):
    # Use a fixed datetime for consistent testing
    fixed_datetime = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    return DomainRequest(
        id=str(ObjectId()),
        requester_id=ObjectId(sample_requester_id),
        company_name="Test Company",
        domains=["example.com", "test.org"],
        purpose="Testing service",
        status=DomainRequestStatus.PENDING,
        created_at=fixed_datetime,
        feedback="This is a default feedback message for testing." # Set a default feedback string with min length
    )

class TestDomainRequestService:

    @pytest.mark.asyncio
    async def test_create_domain_request_success(self, domain_request_service, mock_domain_request_repo, mock_website_repo, sample_domain_request_data, sample_requester_id, sample_domain_request_model):
        mock_website_repo.get_website_by_root_url.return_value = None
        mock_domain_request_repo.create_domain_request.return_value = ObjectId(sample_domain_request_model.id)
        mock_domain_request_repo.get_domain_request_by_id.return_value = sample_domain_request_model.model_dump(by_alias=True)

        with patch('src.services.domain_request_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone # Ensure timezone is accessible

            result = await domain_request_service.create_domain_request(sample_domain_request_data, sample_requester_id)

        assert isinstance(result, DomainRequestResponseSchema)
        assert result.company_name == sample_domain_request_data.company_name
        assert result.domains == sample_domain_request_data.domains
        assert result.status == DomainRequestStatus.PENDING
        assert result.feedback == "This is a default feedback message for testing." # Approved requests should have default feedback
        mock_website_repo.get_website_by_root_url.assert_any_call(sample_domain_request_data.domains[0])
        mock_website_repo.get_website_by_root_url.assert_any_call(sample_domain_request_data.domains[1])
        mock_domain_request_repo.create_domain_request.assert_called_once()
        mock_domain_request_repo.get_domain_request_by_id.assert_called_once_with(str(sample_domain_request_model.id))

    @pytest.mark.asyncio
    async def test_create_domain_request_domain_exists(self, domain_request_service, mock_website_repo, sample_domain_request_data, sample_requester_id):
        mock_website_repo.get_website_by_root_url.side_effect = [{"_id": ObjectId(), "domain": "example.com"}, None]

        with patch('src.services.domain_request_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone

            with pytest.raises(DomainAlreadyExistsError):
                await domain_request_service.create_domain_request(sample_domain_request_data, sample_requester_id)
        mock_website_repo.get_website_by_root_url.assert_called_once_with(sample_domain_request_data.domains[0])

    @pytest.mark.asyncio
    async def test_create_domain_request_invalid_domain_format(self, sample_requester_id):
        from pydantic import ValidationError # Import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            DomainRequestCreateSchema(
                company_name="Invalid Test",
                domains=["invalid-domain"], # Invalid domain format
                purpose="Testing invalid domain"
            )
        assert "Invalid domain format" in str(exc_info.value)
        assert "domains.0" in str(exc_info.value) # Ensure the error is related to the domains field

    @pytest.mark.asyncio
    async def test_get_all_domain_requests_no_filter(self, domain_request_service, mock_domain_request_repo, sample_domain_request_model):
        mock_domain_request_repo.get_all_domain_requests.return_value = [sample_domain_request_model.model_dump(by_alias=True)]

        result = await domain_request_service.get_all_domain_requests()

        assert len(result) == 1
        assert result[0].id == sample_domain_request_model.id
        mock_domain_request_repo.get_all_domain_requests.assert_called_once_with({}, skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_get_all_domain_requests_with_status_filter(self, domain_request_service, mock_domain_request_repo, sample_domain_request_model):
        mock_domain_request_repo.get_all_domain_requests.return_value = [sample_domain_request_model.model_dump(by_alias=True)]

        result = await domain_request_service.get_all_domain_requests(status=DomainRequestStatus.PENDING)

        assert len(result) == 1
        assert result[0].status == DomainRequestStatus.PENDING
        mock_domain_request_repo.get_all_domain_requests.assert_called_once_with({"status": "pending"}, skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_approve_domain_request_success(self, domain_request_service, mock_domain_request_repo, mock_website_repo, sample_domain_request_model, sample_requester_id):
        request_id = sample_domain_request_model.id
        approver_id = str(ObjectId())

        mock_domain_request_repo.get_domain_request_by_id.return_value = sample_domain_request_model.model_dump(by_alias=True)
        mock_website_repo.get_website_by_root_url.return_value = None # Assume domain does not exist

        approved_request_data = sample_domain_request_model.model_dump(by_alias=True)
        approved_request_data["status"] = DomainRequestStatus.APPROVED.value
        approved_request_data["processed_by"] = ObjectId(approver_id)

        with patch('src.services.domain_request_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_dt.utcnow.return_value = datetime(2025, 1, 1, 10, 0, 0)
            mock_dt.timezone = timezone
            approved_request_data["processed_at"] = mock_dt.now(timezone.utc) # Use mocked time for consistency
            mock_domain_request_repo.update_domain_request.return_value = approved_request_data

            result = await domain_request_service.approve_domain_request(request_id, approver_id)

        assert isinstance(result, DomainRequestResponseSchema)
        assert result.id == request_id
        assert result.status == DomainRequestStatus.APPROVED
        assert str(result.processed_by) == approver_id
        mock_domain_request_repo.get_domain_request_by_id.assert_called_once_with(request_id)
        mock_website_repo.get_website_by_root_url.assert_any_call(sample_domain_request_model.domains[0])
        mock_website_repo.create_website.assert_any_call({
            "domain": sample_domain_request_model.domains[0],
            "provider_id": sample_domain_request_model.requester_id,
            "last_checked_at": datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc) # Use mocked time for assertion
        })
        mock_domain_request_repo.update_domain_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_domain_request_not_found(self, domain_request_service, mock_domain_request_repo, sample_requester_id):
        mock_domain_request_repo.get_domain_request_by_id.return_value = None

        with pytest.raises(DomainRequestNotFoundError):
            await domain_request_service.approve_domain_request(str(ObjectId()), sample_requester_id)

    @pytest.mark.asyncio
    async def test_approve_domain_request_not_pending(self, domain_request_service, mock_domain_request_repo, sample_requester_id):
        sample_request = DomainRequest(
            id=str(ObjectId()),
            requester_id=ObjectId(sample_requester_id),
            company_name="Test Company",
            domains=["example.com"],
            purpose="Testing service",
            status=DomainRequestStatus.APPROVED, # Already approved
            created_at=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc), # Use fixed datetime
            feedback="Approved previously with sufficient length." # Add feedback as it's now required and meets length
        )
        mock_domain_request_repo.get_domain_request_by_id.return_value = sample_request.model_dump(by_alias=True)

        with pytest.raises(HTTPException) as exc_info:
            await domain_request_service.approve_domain_request(sample_request.id, sample_requester_id)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Request is not in pending status."

    @pytest.mark.asyncio
    async def test_reject_domain_request_success(self, domain_request_service, mock_domain_request_repo, sample_domain_request_model, sample_requester_id):
        request_id = sample_domain_request_model.id
        approver_id = str(ObjectId())
        feedback = "Not relevant"

        mock_domain_request_repo.get_domain_request_by_id.return_value = sample_domain_request_model.model_dump(by_alias=True)

        rejected_request_data = sample_domain_request_model.model_dump(by_alias=True)
        rejected_request_data["status"] = DomainRequestStatus.REJECTED.value
        rejected_request_data["processed_by"] = ObjectId(approver_id)
        rejected_request_data["feedback"] = feedback # Add this line to set feedback

        with patch('src.services.domain_request_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_dt.utcnow.return_value = datetime(2025, 1, 1, 10, 0, 0)
            mock_dt.timezone = timezone
            rejected_request_data["processed_at"] = mock_dt.now(timezone.utc) # Use mocked time for consistency
            mock_domain_request_repo.update_domain_request.return_value = rejected_request_data

            result = await domain_request_service.reject_domain_request(request_id, approver_id, feedback)

        assert isinstance(result, DomainRequestResponseSchema)
        assert result.id == request_id
        assert result.status == DomainRequestStatus.REJECTED
        assert str(result.processed_by) == approver_id
        assert result.feedback == feedback
        mock_domain_request_repo.get_domain_request_by_id.assert_called_once_with(request_id)
        mock_domain_request_repo.update_domain_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_domain_request_not_found(self, domain_request_service, mock_domain_request_repo, sample_requester_id):
        mock_domain_request_repo.get_domain_request_by_id.return_value = None

        with pytest.raises(DomainRequestNotFoundError):
            await domain_request_service.reject_domain_request(str(ObjectId()), sample_requester_id, "Some feedback")

    @pytest.mark.asyncio
    async def test_reject_domain_request_not_pending(self, domain_request_service, mock_domain_request_repo, sample_requester_id):
        sample_request = DomainRequest(
            id=str(ObjectId()),
            requester_id=ObjectId(sample_requester_id),
            company_name="Test Company",
            domains=["example.com"],
            purpose="Testing service",
            status=DomainRequestStatus.REJECTED, # Already rejected
            created_at=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc), # Use fixed datetime
            feedback="Rejected previously with sufficient length." # Add feedback as it's now required and meets length
        )
        mock_domain_request_repo.get_domain_request_by_id.return_value = sample_request.model_dump(by_alias=True)

        with pytest.raises(HTTPException) as exc_info:
            await domain_request_service.reject_domain_request(sample_request.id, sample_requester_id)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Request is not in pending status."
