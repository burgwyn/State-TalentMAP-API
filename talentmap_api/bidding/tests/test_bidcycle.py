import pytest
import json

from model_mommy.recipe import seq
from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import BidCycle
from talentmap_api.user_profile.models import SavedSearch


@pytest.fixture
def test_bidcycle_fixture(authorized_user):
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", cycle_start_date="2017-01-01", cycle_end_date="2018-01-01", active=True)
    for i in range(5):
        bidcycle.positions.add(mommy.make('position.Position', position_number=seq("2")))

    # Create 5 "in search" positions
    mommy.make('position.Position', position_number=seq("56"), _quantity=5)
    mommy.make('position.Position', position_number=seq("1"), _quantity=2)

    mommy.make('user_profile.SavedSearch',
               id=1,
               name="Test search",
               owner=authorized_user.profile,
               endpoint='/api/v1/position/',
               filters={
                   "position_number__startswith": ["56"],
               })

    # A non-position search
    mommy.make('user_profile.SavedSearch',
               id=2,
               name="Test search",
               owner=authorized_user.profile,
               endpoint='/api/v1/orgpost/',
               filters={
                   "differential_rate__gt": ["0"],
               })


@pytest.mark.django_db(transaction=True)
def test_bidcycle_creation(authorized_client, authorized_user):
    assert BidCycle.objects.all().count() == 0

    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_deadline_date": "1988-02-02",
            "cycle_end_date": "2088-01-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 1
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db(transaction=True)
def test_bidcycle_creation_validation(authorized_client, authorized_user):
    assert BidCycle.objects.all().count() == 0

    # Test end date < start date
    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_deadline_date": "1988-02-02",
            "cycle_end_date": "1088-01-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Test deadline < start date
    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_deadline_date": "1088-02-02",
            "cycle_end_date": "2088-01-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Test end date < deadline
    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_deadline_date": "1988-03-02",
            "cycle_end_date": "1988-02-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_patch(authorized_client, authorized_user):
    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_end_date": "2088-01-01",
            "active": True
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert BidCycle.objects.all().count() == 1
    cycle = BidCycle.objects.get(id=1)
    assert cycle.name == "bidcycle"
    assert str(cycle.cycle_start_date) == "1988-01-01"
    assert str(cycle.cycle_end_date) == "2088-01-01"
    assert cycle.active


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_patch_validation(authorized_client, authorized_user):
    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "cycle_end_date": "1088-01-01",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "cycle_start_date": "9999-01-01",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_list_positions(authorized_client, authorized_user):
    response = authorized_client.get('/api/v1/bidcycle/1/positions/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 5


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_actions(authorized_client, authorized_user):
    position = mommy.make('position.Position')

    # Check the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Add the position to the bidcycle
    response = authorized_client.put(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Remove the position from the bidcycle
    response = authorized_client.delete(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_batch_actions(authorized_client, authorized_user):
    mommy.make(BidCycle, id=2, name="Bidcycle 2", cycle_start_date="2017-01-01", cycle_end_date="2018-01-01")
    # Try to add a saved search batch that isn't positions
    response = authorized_client.put(f'/api/v1/bidcycle/2/position/batch/2/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Add the position batch to the bidcycle
    response = authorized_client.put(f'/api/v1/bidcycle/2/position/batch/1/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check that we've added the positions
    response = authorized_client.get('/api/v1/bidcycle/2/positions/')

    assert response.status_code == status.HTTP_200_OK

    savedsearch = SavedSearch.objects.get(id=1)
    savedsearch.update_count()
    savedsearch.refresh_from_db()

    assert len(response.data["results"]) == savedsearch.count


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_current_cycle_available_filter(authorized_client, authorized_user):
    # Add a handshake bid
    bidcycle = BidCycle.objects.first()
    mommy.make('bidding.Bid', bidcycle=bidcycle, status="handshake_offered", position=bidcycle.positions.first(), user=authorized_user.profile)

    response = authorized_client.get(f'/api/v1/position/?is_available_in_current_bidcycle=true')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 4

    response = authorized_client.get(f'/api/v1/position/?is_available_in_current_bidcycle=false')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
