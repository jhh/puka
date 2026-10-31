# Item categories

Status: proposed on 2026-10-31. Not implemented.

## Goal

Add a drop-down next to the search box on the inventory list (`/stuff/`)
that limits the list, and any search, to one category such as
Electronics, Tools, or Hardware. Each `stuff.Item` belongs to a single
category.

## Decision

Add a `Category` model and give `Item` a nullable foreign key to it. Do
not reuse taggit tags as hard-coded categories.

### Why not reserved tags

- **No single-category guarantee.** `Item.tags` is many-to-many, so an
  item could carry both `electronics` and `tools`. The rule would have
  to be enforced by hand in the form, the CSV importer, the admin, and
  the shell.
- **Categories and tags would mix.** Tags are free-form, so a category
  would only be a tag that the code treats specially. Typos and case
  variants slip in, and taggit's `Tag` table is shared with bookmarks
  (`services.py` adds a `stuff` tag). The item tag cloud
  (`/stuff/item/tags/`) would also need to hide category tags.
- **Weaker filtering.** Filtering would join through `TaggedItem` and
  match on tag name, instead of an indexed `category_id = ?` check.
- **No source for the drop-down.** A hard-coded list of names in code
  would have to stay in sync with tag rows in the database.

Tags remain the right tool for loose, overlapping labels. A category is
a single attribute, and a foreign key models it directly.

### Foreign key vs. a fixed list of choices

- **`Category` model + FK.** Pros: edit in the admin, rename in one
  place, `on_delete=PROTECT`, room for a sort order or icon later.
  Cons: one more table and migration.
- **`CharField(choices=...)`.** Pros: simplest, no join. Cons: a new or
  renamed category needs a code change, a deploy, and a data migration.

The category list is expected to grow, so the foreign key fits better.

## Plan

1. **Model** (`puka/stuff/models.py`):
   - `Category` with a unique `name` and an optional `slug`, ordered by
     name, with a natural key to match `Item`.
   - On `Item`:
     `category = ForeignKey(Category, null=True, blank=True, on_delete=PROTECT, related_name="items")`. Allowing empty values
     lets existing items migrate without a category.
2. **Migrations:**
   - A schema migration.
   - Optionally, a data migration that seeds starter categories, or
     assigns them from existing tags that already act as categories.
3. **Manager:** keep `ItemManager.search()` unchanged and add
   `with_category()`. The view applies the category filter after the
   search, so it composes with plain text, `#tag`, and `@location`
   searches.
4. **View** (`ItemListView.get_queryset` in
   `puka/stuff/views/item.py`):
   - Read `?category=<id or slug>` and filter on it.
   - Add `select_related("category")`.
   - Put the categories and the selected category in the context.
5. **Template** (`puka/templates/stuff/item_list.html`):
   - A daisyUI `select` inside the same search form, joined to the
     search input.
   - Changing it fires the same htmx request into `#item-results`, so
     the query and the category stay in the URL together.
6. **Form, importer, and admin:**
   - Add `category` to `ItemForm`.
   - Add a "Category" column to the CSV import
     (`puka/stuff/importer.py`), matched by name.
   - Register `Category` in the admin.
   - Optionally show the category on the item detail page and in list
     rows.
7. **Tests:** model and manager filtering, the list view combined with
   each search type, the item form, and the importer column.

## Open questions

1. **Who manages categories?** Admin only, or an in-app page to add and
   rename them?
2. **Uncategorized items:** allow items without a category, with "All"
   and possibly "Uncategorized" options in the drop-down? Or require a
   category once existing items are backfilled?
3. **Nesting:** are subcategories needed (e.g. Hardware > Fasteners)? If
   so, the treebeard `MP_Node` pattern used by `Location` could apply.
   Start with a flat list unless nesting is needed.
4. **Backfill:** do any current tags already act as categories, so the
   data migration could convert them?
