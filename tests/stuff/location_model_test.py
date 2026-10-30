from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from puka.stuff.models import Location

if TYPE_CHECKING:
    from django.db import models


def test_location_path_uses_c_collation():
    # treebeard paths are base62: "Z" sorts before "a" only in C collation.
    path = cast("models.CharField", Location._meta.get_field("path"))  # noqa: SLF001
    assert path.db_collation == "C"


@pytest.mark.django_db
def test_location_add_child_after_lowercase_path():
    root = Location.objects.add_root({"name": "Root", "code": "R"})
    parent = Location.objects.add_child(root, {"name": "Parent", "code": "R-P"})
    for name, position in (("A", "000Z"), ("B", "000a")):
        Location.objects.create(
            name=name,
            code=f"R-P-{name}",
            path=parent.path + position,
            depth=parent.depth + 1,
            numchild=0,
        )
    Location.objects.filter(pk=parent.pk).update(numchild=2)

    child = Location.objects.add_child(
        Location.objects.get(pk=parent.pk),
        {"name": "C", "code": "R-P-C"},
    )

    assert child.path == parent.path + "000b"


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
