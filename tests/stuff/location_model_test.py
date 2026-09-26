import pytest

from puka.stuff.models import Location


@pytest.mark.django_db
def test_location_roots_ordered_by_name():
    garage = Location.objects.add_root({"name": "Garage", "code": "G"})
    Location.objects.add_root({"name": "Closet", "code": "C"})
    Location.objects.add_root({"name": "Shed", "code": "S"})
    Location.objects.add_sibling(
        Location.objects.get(pk=garage.pk),
        create_kwargs={"name": "Pantry", "code": "P"},
    )

    roots = list(Location.objects.get_root_nodes())
    assert len(roots) == 4
    assert roots[0].name == "Closet"
    assert roots[1].name == "Garage"
    assert roots[2].name == "Pantry"
    assert roots[3].name == "Shed"
