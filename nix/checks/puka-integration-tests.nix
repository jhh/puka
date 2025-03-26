{
  flake,
  pkgs,
  ...
}:
let
  secrets = pkgs.writeText "puka-test-secrets" ''
    DJANGO_DATABASE_URL="postgres:///puka"
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
    SECRET_KEY="test-secret-key"
  '';
in
pkgs.nixosTest {
  name = "puka-integration-tests";

  nodes.machine =
    { pkgs, ... }:
    {
      imports = [
        flake.modules.nixos.puka
      ];

      environment.systemPackages = with pkgs; [
        wget
      ];

      services.puka = {
        enable = true;
        secrets = [ secrets ];
        port = 8001;
      };

      services.postgresql = {
        enable = true;
        package = pkgs.postgresql_16;
        ensureDatabases = [ "puka" ];
        ensureUsers = [
          {
            name = "puka";
            ensureDBOwnership = true;
          }
        ];
      };

      system.stateVersion = "24.11";
    };

  testScript =
    { nodes, ... }:
    let
      inherit (nodes.machine.services.puka) port venv;
    in
    ''
      import random
      import string

      def generate_random_string(length):
          characters = string.ascii_letters + string.digits
          return "".join(random.choice(characters) for i in range(length))

      base_url = "http://localhost:${toString port}"
      login_url = f"{base_url}/admin/login/"
      cookie_jar_path = "/tmp/cookies.txt"
      curl = f"curl --cookie {cookie_jar_path} --cookie-jar {cookie_jar_path} --fail --show-error --silent"

      # wait for service
      machine.wait_for_unit("puka.service")
      machine.wait_until_succeeds(f"{curl} -sLf {login_url}")

      # check for missing static files
      machine.succeed(f"wget -nv --level=1 --spider --recursive {login_url}")

      # create a superuser
      username = "username"
      password = "password"

      machine.succeed(f"""
        sudo -u puka env \
        DJANGO_SETTINGS_MODULE=puka.settings.production \
        SECRET_KEY=test \
        DJANGO_SUPERUSER_PASSWORD='{password}' \
        ${venv}/bin/puka-manage createsuperuser --no-input --username='{username}' --email=nobody@j3ff.io
        """
      )

      # log in as superuser
      csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
      machine.succeed(f"""
        {curl} \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'username={username}' \
        --data 'password={password}' \
        {login_url}
        """
      )

      # test that main bookmarks list is available
      assert "New Bookmark" in machine.succeed(f"{curl} --location {base_url}"), "T001"

      # create a new bookmark

      title = generate_random_string(50)
      csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
      machine.succeed(f"""
        {curl} -X POST \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'title={title}' \
        --data 'description=' \
        --data-urlencode 'url=http://example.com' \
        --data 'tags=foobar' \
        --data 'active=on' \
        {base_url}/bookmarks/new/
        """
      )

      # check for this new bookmark in main bookmark list
      output = machine.succeed(f"{curl} --location {base_url}")
      assert title in output, "T002"
      assert "http://example.com" in output, "T003"
      assert "foobar" in output, "T004"

      # seed locations
      machine.succeed("""
        sudo -u puka env \
        DJANGO_SETTINGS_MODULE=puka.settings.production \
        SECRET_KEY=test \
        ${venv}/bin/puka-manage seed_locations
        """
      )

      location_code = "S-D01-08"

      # check for this new bookmark in main locations list
      output = machine.succeed(f"{curl} --location {base_url}/stuff/location/23/")
      assert location_code in output, "T005"

      # create a new item

      name = generate_random_string(50)
      notes = generate_random_string(50)
      tags = f"{generate_random_string(3)} {generate_random_string(5)} {generate_random_string(7)}"
      reorder_level = random.randint(0, 100)
      location_code = "S-A01"
      quantity = random.randint(0, 100)
      bookmark_url = f"https://example.com/{generate_random_string(10)}"
      csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
      machine.succeed(f"""
        {curl} -X POST \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'name={name}' \
        --data 'notes={notes}' \
        --data 'tags={tags}' \
        --data 'reorder_level={reorder_level}' \
        --data 'location_code={location_code}' \
        --data 'quantity={quantity}' \
        --data 'bookmark_url={bookmark_url}' \
        {base_url}/stuff/item/new/
        """
      )

      # check for this new item in item detail page
      output = machine.succeed(f"{curl} --location {base_url}/stuff/1/")
      assert name in output, "T006"
      assert notes in output, "T007"
      for tag in tags.split():
          assert tag in output, f"T008-{tag}"
      assert str(reorder_level) in output, "T009"
      assert location_code in output, "T010"
      assert str(quantity) in output, "T011"
      assert bookmark_url in output, "T012"

    '';
}
