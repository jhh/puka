# type: ignore
# ruff: noqa: F821, INP001, PGH003, S101, S108, S311
import random
import re
import string

from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:${port}"
COOKIE_JAR_PATH = "/tmp/cookies.txt"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


def get_csrf_token(url):
    html = machine.succeed(f"{CURL} -sLf {url}")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("input", {"name": "csrfmiddlewaretoken"})
    assert element is not None, "get_csrf_token: token not found"
    return element["value"]


CURL = (
    f"curl --cookie {COOKIE_JAR_PATH} --cookie-jar {COOKIE_JAR_PATH} --fail --show-error --silent"
)

# wait for service
machine.wait_for_unit("puka.service")
machine.succeed("rm -f /tmp/cookies.txt")
machine.wait_until_succeeds(f"curl --fail --silent {BASE_URL}/accounts/login/ -o /dev/null")

with subtest("create superuser account"):
    machine.succeed("${createSuperUser}")

with subtest("log in as superuser"):
    csrf_token = get_csrf_token(f"{BASE_URL}/accounts/login/")
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
    csrf_token = get_csrf_token(f"{BASE_URL}/bookmarks/new/")

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
    inventory_name = generate_random_string(50)
    inventory_notes = generate_random_string(150)
    inventory_tags = (
        f"{generate_random_string(3)} {generate_random_string(5)} {generate_random_string(7)}"
    )
    reorder_level = random.randint(0, 100)
    location_code = "S-A01"
    quantity = random.randint(0, 100)
    bookmark_url = f"https://example.com/{generate_random_string(10)}"

    csrf_token = get_csrf_token(f"{BASE_URL}/stuff/item/new/")

    machine.succeed(f"""
        {CURL} -v \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'name={inventory_name}' \
        --data 'notes={inventory_notes}' \
        --data 'tags={inventory_tags}' \
        --data 'reorder_level={reorder_level}' \
        --data 'location_code={location_code}' \
        --data 'quantity={quantity}' \
        --data-urlencode 'bookmark_url={bookmark_url}' \
        {BASE_URL}/stuff/item/new/
        """)

    # find the url to the item posted
    html = machine.succeed(f"{CURL} --location {BASE_URL}/stuff/")
    soup = BeautifulSoup(html, "html.parser")
    item = soup.find("a", href=re.compile(r"^/stuff/item/\d+/$"))
    assert item is not None, "create inventory: element not found"
    assert item.get_text(strip=True) == inventory_name, "create inventory: list does not match"
    item_url = item["href"]

    # check for this new item in item detail page
    html = machine.succeed(f"{CURL} --location {BASE_URL}{item_url}")
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()

    assert inventory_name in page_text, "create inventory: name does not match"
    assert inventory_notes in page_text, "create inventory: notes do not match"

    for tag in inventory_tags.split():
        assert tag in page_text, f"create inventory: {tag} does not match"

    assert str(reorder_level) in page_text, "create inventory: reorder_level does not match"
    assert location_code in page_text, "create inventory: location_code does not match"
    assert str(quantity) in page_text, "create inventory: quantity does not match"
    links = [a["href"] for a in soup.find_all("a", href=True)]
    assert bookmark_url in links, "create inventory: bookmark URL does not match"

with subtest("create area"):
    area_name = generate_random_string(50)
    area_notes = generate_random_string(150)

    csrf_token = get_csrf_token(f"{BASE_URL}/upkeep/area/new/")

    html = machine.succeed(f"""
        {CURL} -v -L \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'name={area_name}' \
        --data 'notes={area_notes}' \
        {BASE_URL}/upkeep/area/new/
        """)

    soup = BeautifulSoup(html, "html.parser")
    area = soup.find("a", href=re.compile(r"^/upkeep/area/\d+/$"))
    assert area is not None, "create inventory: element not found"
    assert area.get_text(strip=True) == area_name, "create area: list does not match"
    area_url = area["href"]

    # check for this new area in area detail page
    html = machine.succeed(f"{CURL} {BASE_URL}{area_url}")
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()
    assert area_name in page_text, "create area: name does not match"
    assert area_notes in page_text, "create area: notes do not match"


with subtest("create upkeep task"):
    task_name = generate_random_string(50)
    task_notes = generate_random_string(150)
    interval = random.randint(1, 12)

    csrf_token = get_csrf_token(f"{BASE_URL}/upkeep/task/new/")

    html = machine.succeed(f"""
        {CURL} -v -L \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'name={task_name}' \
        --data 'area=1' \
        --data 'interval={interval}' \
        --data 'frequency=months' \
        --data 'notes={task_notes}' \
        {BASE_URL}/upkeep/task/new/
        """)

    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()
    assert task_name in page_text, "create upkeep task: name does not match"
    assert task_notes in page_text, "create upkeep task: notes do not match"
    assert str(interval) in page_text, "create upkeep task: interval does not match"


with subtest("create schedule"):
    due_date = "2026-06-01"
    schedule_notes = generate_random_string(150)
    task_pk = 1

    csrf_token = get_csrf_token(f"{BASE_URL}/upkeep/task/{task_pk}/schedule/new/")

    html = machine.succeed(f"""
        {CURL} -v -L \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'task={task_pk}' \
        --data 'due_date={due_date}' \
        --data 'notes={schedule_notes}' \
        {BASE_URL}/upkeep/task/{task_pk}/schedule/new/
        """)

    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()
    assert "June 1, 2026" in page_text, "create schedule: due_date does not match"
    assert schedule_notes in page_text, "create schedule: notes do not match"
