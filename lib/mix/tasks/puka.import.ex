defmodule Mix.Tasks.Puka.Import do
  @shortdoc "Imports a Bookmarks CSV file"
  @moduledoc """
  Imports the bookmarks from a CSV file.

  Here is an example:

      $ mix puka.import /path/to/bookmarks.csv

  """
  @requirements ["app.start"]
  use Mix.Task

  import Ecto.Changeset
  alias Puka.Bookmarks.Bookmark
  alias Puka.Tags
  alias Puka.Repo

  def run(args) do
    Logger.configure(level: :info)
    IO.puts("Importing Bookmarks CSV file...")

    File.stream!(hd(args))
    |> CSV.decode(headers: true)
    |> Enum.map(&parse_row/1)
    |> Enum.map(&changeset_with_timestamps/1)
    |> Enum.each(&Repo.insert/1)
  end

  defp parse_row({:ok, row}) do
    {:ok, inserted_at, 0} = DateTime.from_iso8601(row["created_utc"])
    {:ok, updated_at, 0} = DateTime.from_iso8601(row["modified_utc"])

    row
    |> Map.put("active", row["active"] == "t")
    |> Map.put("inserted_at", inserted_at)
    |> Map.put("updated_at", updated_at)
  end

  defp parse_row({:error, msg}) do
    IO.puts(:stderr, msg)
  end

  def changeset_with_timestamps(attrs) do
    %Bookmark{}
    |> cast(attrs, [:title, :description, :url, :active])
    |> validate_required([:title, :url])
    |> unique_constraint(:url)
    |> put_change(:inserted_at, attrs["inserted_at"])
    |> put_change(:updated_at, attrs["updated_at"])
    |> Ecto.Changeset.put_assoc(:tags, Tags.parse_tags(attrs))
  end
end
