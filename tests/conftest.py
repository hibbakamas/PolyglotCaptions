import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import caption as caption_router
from app.routers import manual as manual_router

# -------------------------------------------
# AUTH OVERRIDE FOR TESTS
# -------------------------------------------


def override_get_current_user():
    # Always pretend "testuser" is authenticated
    return "testuser"


# OVERRIDE FOR /api/captions
app.dependency_overrides[caption_router.get_current_user] = override_get_current_user

# OVERRIDE FOR /api/manual

app.dependency_overrides[manual_router.get_current_user] = override_get_current_user


# -------------------------------------------
# TEST CLIENT FIXTURE
# -------------------------------------------


@pytest.fixture
def client():
    return TestClient(app)
