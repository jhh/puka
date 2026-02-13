defmodule Puka.Repo do
  use Ecto.Repo,
    otp_app: :puka,
    adapter: Ecto.Adapters.Postgres
end
