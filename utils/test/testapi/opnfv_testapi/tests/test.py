import pytest
import uuid


@pytest.fixture
def mocked_uuid(mocker):
    mock_uuid = mocker.patch.object(uuid, 'uuid4', autospec=True)
    mock_uuid.return_value = uuid.UUID(hex='5ecd5827b6ef4067b5ac3ceac07dde9f')
    return mock_uuid


def test_mockers(mocked_uuid):
    # this would return a different value if this wasn't the case
    assert uuid.uuid4().hex == '5ecd5827b6ef4067b5ac3ceac07dde9f'