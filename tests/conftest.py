import pytest
from fastapi.testclient import TestClient
from app.main import app

# -------------------------------------------
# AUTH OVERRIDE FOR TESTS
# -------------------------------------------

def override_get_current_user():
    # Always pretend "testuser" is authenticated
    return "testuser"


# OVERRIDE FOR /api/captions
import app.routers.caption as caption_router
app.dependency_overrides[caption_router.get_current_user] = override_get_current_user

# OVERRIDE FOR /api/manual
import app.routers.manual as manual_router
app.dependency_overrides[manual_router.get_current_user] = override_get_current_user


# -------------------------------------------
# TEST CLIENT FIXTURE
# -------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)
