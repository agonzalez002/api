import uuid
import pytest

from glados import constants
from glados.models import Entity, Room


@pytest.fixture
def entities():
    kitchen = Room(id=uuid.UUID(int=1), name="Kitchen")
    kitchen.save(commit=False)

    living_room = Room(id=uuid.UUID(int=2), name="Living Room")
    living_room.save(commit=False)

    entity = Entity(
        id=uuid.UUID(int=1),
        name="Ceiling Light",
        type=constants.EntityType.light.name,
        status=constants.EntityStatus.off.name,
        value=None,
        room_id=kitchen.id)
    entity.save(commit=False)

    entity = Entity(
        id=uuid.UUID(int=2),
        name="Lamp",
        type=constants.EntityType.light.name,
        status=constants.EntityStatus.on.name,
        value=200,
        room_id=living_room.id)
    entity.save(commit=False)

    entity = Entity(
        id=uuid.UUID(int=3),
        name="Thermometer",
        type=constants.EntityType.sensor.name,
        status=constants.EntityStatus.on.name,
        value=28,
        room_id=living_room.id)
    entity.save(commit=False)


def test_get_entities_with_invalid_data(client):
    response = client.get("/entities?type=invalid")

    assert response.status_code == 422
    assert response.json == {"errors": {
        "type": ["Must be one of: sensor, light, switch, multimedia, air_conditioner."]
    }}


def test_get_entities(client, entities, mocker):
    response = client.get("/entities")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Ceiling Light",
            "type": "light",
            "status": "off",
            "value": None,
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000001',
                'name': 'Kitchen'
            }
        },
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "name": "Lamp",
            "type": "light",
            "status": "on",
            "value": "200",
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000002',
                'name': 'Living Room'
            }
        },
        {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "Thermometer",
            "type": "sensor",
            "status": "on",
            "value": "28",
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000002',
                'name': 'Living Room'
            }
        }
    ]


def test_get_entities_with_type_filter(client, entities, mocker):
    response = client.get("/entities?type=sensor")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "Thermometer",
            "type": "sensor",
            "status": "on",
            "value": "28",
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000002',
                'name': 'Living Room'
            }
        }
    ]


def test_get_entities_with_status_filter(client, entities, mocker):
    """Test for filter on entity status."""
    response = client.get("/entities?status=on")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "name": "Lamp",
            "type": "light",
            "status": "on",
            "value": "200",
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000002',
                'name': 'Living Room'
            }
        },
        {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "Thermometer",
            "type": "sensor",
            "status": "on",
            "value": "28",
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000002',
                'name': 'Living Room'
            }
        },
    ]


def test_get_entities_with_room_filter(client, entities, mocker):
    """Test for filter on entity name."""
    response = client.get("/entities?room=Kitchen")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Ceiling Light",
            "type": "light",
            "status": "off",
            "value": None,
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000001',
                'name': 'Kitchen'
            }
        },
    ]


def test_get_entities_with_two_filters(client, entities, mocker):
    """Test for firter on entity with two parameters."""
    response = client.get("/entities?status=off&room=Kitchen")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Ceiling Light",
            "type": "light",
            "status": "off",
            "value": None,
            "created_at": mocker.ANY,
            "room": {
                'id': '00000000-0000-0000-0000-000000000001',
                'name': 'Kitchen'
            }
        },
    ]


def test_patch_entities_with_type_filters(client, entities):
    response = client.patch('/entity/00000000-0000-0000-0000-000000000001', json={'type': "sensor"})

    assert response.status_code == 200

    entity = Entity.query.get('00000000-0000-0000-0000-000000000001')
    assert entity.type == "sensor"


def test_patch_entities_without_wrong_id(client, entities):
    response = client.patch('/entity/12', json={'type': "sensor"})

    assert response.status_code == 500
    print(response.json)
    assert response.json == {'error': 'internal_error', 'message': 'Internal error.'}


def test_patch_entities_with_room_filters(client, entities):
    response = client.patch('/entity/00000000-0000-0000-0000-000000000001', json={'room': "00000000-0000-0000-0000-000000000002"})

    assert response.status_code == 200

    entity = Entity.query.get('00000000-0000-0000-0000-000000000001')
    print(entity.room_id)
    assert entity.room_id == uuid.UUID(int=2)
