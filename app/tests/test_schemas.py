import pytest
from datetime import datetime
from pydantic import ValidationError

# Importing your schemas (ensure paths match your project structure)
from app.schemas.target import TargetCreate, TargetResponse
from app.schemas.domain import DomainCreate
from app.schemas.ip import IPAddressResponse


# --- Target Schema Tests ---

def test_target_create_valid():
    """
    Test that TargetCreate accepts a valid name and correctly assigns it.
    """
    payload = {"name": "External_Infrastructure"}
    schema = TargetCreate(**payload)

    assert schema.name == "External_Infrastructure"


def test_target_create_invalid_empty():
    """
    Test that TargetCreate raises a ValidationError if the name is empty.
    (Assuming min_length=1 is set in your Pydantic model)
    """
    with pytest.raises(ValidationError):
        TargetCreate(name="")


def test_target_read_from_orm():
    """
    Test that TargetResponse can correctly parse and validate data coming 
    from a database model (ORM mode).
    """
    # Simulating data as it would come from an SQLAlchemy model
    orm_data = {
        "id": 10,
        "name": "Production_Server",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    schema = TargetResponse.model_validate(orm_data)

    assert schema.id == 10
    assert schema.name == "Production_Server"
    assert schema.status == "active"


# --- Domain Schema Tests ---

def test_domain_create_logic():
    """
    Validate that DomainCreate links to a target_id and has a proper domain string.
    """
    payload = {"domain_name": "google.com", "target_id": 5}
    schema = DomainCreate(**payload)

    assert schema.domain_name == "google.com"
    assert schema.target_id == 5


def test_domain_create_wrong_id_type():
    """
    Ensure the schema rejects non-integer target IDs.
    """
    with pytest.raises(ValidationError):
        DomainCreate(domain_name="test.com", target_id="five")


# --- IP and Scan Details Schema Tests ---

def test_ip_read_validation():
    """
    Verify that the IP schema correctly validates IPv4 formats.
    """
    # Valid IPv4
    valid_data = {
        "id": 1,
        "ip": "8.8.8.8",
        "version": "ipv4",
        "domain_id": 1
    }
    schema = IPAddressResponse.model_validate(valid_data)
    assert str(schema.ip) == "8.8.8.8"


# def test_ip_read_invalid_format():
#     """
#     Check that Pydantic's built-in network validation catches bad IP strings.
#     """
#     invalid_data = {
#         "id": 1,
#         "ip": "999.0.0.1",
#         "version": "ipv4",
#         "domain_id": 1
#     }
#     with pytest.raises(ValidationError):
#         IPAddressResponse.model_validate(invalid_data)