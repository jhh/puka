import pytest

from puka.upkeep.models import Area, Task
from puka.upkeep.services import search_areas_and_tasks


@pytest.mark.django_db
class TestSearch:
    def test_area_search_success(self, area):
        results = search_areas_and_tasks("test")
        assert len(results) == 1
        assert results[0].name == area.name

    @pytest.mark.usefixtures("area")
    def test_area_search_fail(self):
        results = search_areas_and_tasks("fail")
        assert len(results) == 0

    def test_task_test_success(self, task):
        result = search_areas_and_tasks("area")
        assert len(result) == 1
        assert isinstance(result[0], Area)
        assert result[0].name == task.area.name

        result = search_areas_and_tasks("task")
        assert len(result) == 1
        assert isinstance(result[0], Task)
        assert result[0].name == task.name

        result = search_areas_and_tasks("test")
        assert len(result) == 2
        types = [r.model_name for r in result]
        assert "area" in types
        assert "task" in types
