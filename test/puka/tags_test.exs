defmodule Puka.TagsTest do
  use Puka.DataCase

  alias Puka.Tags

  describe "tags" do
    alias Puka.Tags.Tag

    import Puka.TagsFixtures

    @invalid_attrs %{name: nil}

    test "list_tags/0 returns all tags" do
      tag = tag_fixture()
      assert Tags.list_tags() == [tag]
    end

    test "get_tag!/1 returns the tag with given id" do
      tag = tag_fixture()
      assert Tags.get_tag!(tag.id) == tag
    end

    test "create_tag/1 with valid data creates a tag" do
      valid_attrs = %{name: "some name"}

      assert {:ok, %Tag{} = tag} = Tags.create_tag(valid_attrs)
      assert tag.name == "some name"
    end

    test "create_tag/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Tags.create_tag(@invalid_attrs)
    end

    test "update_tag/2 with valid data updates the tag" do
      tag = tag_fixture()
      update_attrs = %{name: "some updated name"}

      assert {:ok, %Tag{} = tag} = Tags.update_tag(tag, update_attrs)
      assert tag.name == "some updated name"
    end

    test "update_tag/2 with invalid data returns error changeset" do
      tag = tag_fixture()
      assert {:error, %Ecto.Changeset{}} = Tags.update_tag(tag, @invalid_attrs)
      assert tag == Tags.get_tag!(tag.id)
    end

    test "delete_tag/1 deletes the tag" do
      tag = tag_fixture()
      assert {:ok, %Tag{}} = Tags.delete_tag(tag)
      assert_raise Ecto.NoResultsError, fn -> Tags.get_tag!(tag.id) end
    end

    test "change_tag/1 returns a tag changeset" do
      tag = tag_fixture()
      assert %Ecto.Changeset{} = Tags.change_tag(tag)
    end
  end

  describe "list_tags/3 with :paged" do
    import Puka.TagsFixtures

    test "returns paginated results with correct structure" do
      tag = tag_fixture()
      result = Tags.list_tags(:paged, 1, 5)

      assert result.page == 1
      assert result.count == 1
      assert result.has_next == false
      assert result.has_prev == false
      assert result.prev_page == nil
      assert result.next_page == nil
      assert result.first == 1
      assert result.last == 1
      assert length(result.list) == 1
      assert hd(result.list).id == tag.id
    end

    test "returns correct pagination for multiple pages" do
      for i <- 1..25 do
        tag_fixture(%{name: "tag #{i}"})
      end

      result = Tags.list_tags(:paged, 1, 10)

      assert result.page == 1
      assert result.count == 25
      assert result.has_next == true
      assert result.has_prev == false
      assert result.prev_page == nil
      assert result.next_page == 2
      assert result.first == 1
      assert result.last == 10
      assert length(result.list) == 10

      result = Tags.list_tags(:paged, 2, 10)

      assert result.page == 2
      assert result.has_next == true
      assert result.has_prev == true
      assert result.prev_page == 1
      assert result.next_page == 3
      assert result.first == 11
      assert result.last == 20
      assert length(result.list) == 10

      result = Tags.list_tags(:paged, 3, 10)

      assert result.page == 3
      assert result.has_next == false
      assert result.has_prev == true
      assert result.prev_page == 2
      assert result.next_page == nil
      assert result.first == 21
      assert result.last == 25
      assert length(result.list) == 5
    end

    test "respects per_page parameter" do
      for i <- 1..8 do
        tag_fixture(%{name: "tag #{i}"})
      end

      result = Tags.list_tags(:paged, 1, 3)

      assert result.count == 8
      assert result.has_next == true
      assert length(result.list) == 3

      result = Tags.list_tags(:paged, 3, 3)

      assert result.has_next == false
      assert length(result.list) == 2
    end

    test "returns empty list for page beyond results" do
      tag_fixture()

      result = Tags.list_tags(:paged, 5, 10)

      assert result.count == 1
      assert result.has_next == false
      assert result.has_prev == true
      assert result.list == []
    end

    test "handles string page number" do
      tag_fixture()

      result = Tags.list_tags(:paged, "1", 10)

      assert result.page == 1
    end
  end
end
