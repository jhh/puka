# type: ignore
# ruff: noqa: F821, INP001, PGH003, S101, S108, S311
import random
import string

from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:${port}"
COOKIE_JAR_PATH = "/tmp/cookies.txt"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


CURL = (
    f"curl --cookie {COOKIE_JAR_PATH} --cookie-jar {COOKIE_JAR_PATH} --fail --show-error --silent"
)

# wait for service
machine.wait_for_unit("puka.service")
machine.succeed("rm -f /tmp/cookies.txt")
machine.wait_until_succeeds(f"curl --fail --silent {BASE_URL}/accounts/login/ -o /dev/null")

with subtest("create superuser account"):
    machine.succeed("${createSuperUser}")

html = machine.succeed(f"{CURL} -sLf {BASE_URL}/accounts/login/")
soup = BeautifulSoup(html, "html.parser")
csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

with subtest("log in as superuser"):
    machine.succeed(f"""
    {CURL} -v \
    -H "Referer: {BASE_URL}/accounts/login/" \
    --data "csrfmiddlewaretoken={csrf_token}" \
    --data "username=${username}" \
    --data "password=${password}" \
    {BASE_URL}/accounts/login/
    """)

html = machine.succeed(f"{CURL} -sLf {BASE_URL}/")
soup = BeautifulSoup(html, "html.parser")
stylesheets = soup.find_all("link", rel="stylesheet")
puka_stylesheet_url = stylesheets[1]["href"]
puka_script_url = soup.find("script", {"defer": True})["src"]


with subtest("check static files"):
    assert "puka" in puka_stylesheet_url, "check static files: parsed wrong stylesheet URL"
    assert "puka" in puka_script_url, "check static files: parsed wrong script URL"
    machine.succeed(f"{CURL} {BASE_URL}{puka_stylesheet_url}")
    machine.succeed(f"{CURL} {BASE_URL}{puka_script_url}")


with subtest("create a bookmark"):
    title = generate_random_string(50)
    description = generate_random_string(150)
    html = machine.succeed(f"{CURL} -sLf {BASE_URL}/bookmarks/new/")
    soup = BeautifulSoup(html, "html.parser")
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    # post bookmark and redirect to bookmarks
    html = machine.succeed(f"""
        {CURL} -v -L \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'title={title}' \
        --data 'description={description}' \
        --data-urlencode 'url=http://example.com' \
        --data 'tags=foobar,quux' \
        --data 'active=on' \
        {BASE_URL}/bookmarks/new/
        """)

    # check for this new bookmark in main bookmark list
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()

    assert title in page_text, "create bookmark: title does not match"
    assert description in page_text, "create bookmark: description does not match"

    links = [a["href"] for a in soup.find_all("a", href=True)]
    assert "http://example.com" in links, "create bookmark: URL does not match"

    tags = [tag.get_text(strip=True) for tag in soup.find_all("a")]
    assert "foobar" in tags, "create bookmark: tag 'foobar' does not match"
    assert "quux" in tags, "create bookmark: tag 'quux' does not match"


with subtest("seed locations"):
    machine.succeed("puka-manage seed_locations")
    location_code = "S-D01-08"

    # check for this new location in main locations list
    html = machine.succeed(f"{CURL} {BASE_URL}/stuff/location/23/")
    assert location_code in html, "T005"


with subtest("create inventory"):
    name = generate_random_string(50)
    notes = generate_random_string(50)
    tags = f"{generate_random_string(3)} {generate_random_string(5)} {generate_random_string(7)}"
    reorder_level = random.randint(0, 100)
    location_code = "S-A01"
    quantity = random.randint(0, 100)
    bookmark_url = f"https://example.com/{generate_random_string(10)}"

    html = machine.succeed(f"{CURL} -sLf {BASE_URL}/stuff/item/new/")
    soup = BeautifulSoup(html, "html.parser")
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    machine.succeed(f"""
        {CURL} -v \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'name={name}' \
        --data 'notes={notes}' \
        --data 'tags={tags}' \
        --data 'reorder_level={reorder_level}' \
        --data 'location_code={location_code}' \
        --data 'quantity={quantity}' \
        --data-urlencode 'bookmark_url={bookmark_url}' \
        {BASE_URL}/stuff/item/new/
        """)

    # check for this new item in item detail page
    html = machine.succeed(f"{CURL} --location {BASE_URL}/stuff/item/1/")
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()

    assert name in page_text, "create inventory: name does not match"
    assert notes in page_text, "create inventory: notes do not match"

    for tag in tags.split():
        assert tag in page_text, f"create inventory: {tag} does not match"

    assert str(reorder_level) in page_text, "create inventory: reorder_level does not match"
    assert location_code in page_text, "create inventory: location_code does not match"
    assert str(quantity) in page_text, "create inventory: quantity does not match"
    links = [a["href"] for a in soup.find_all("a", href=True)]
    assert bookmark_url in links, "create inventory: bookmark URL does not match"
