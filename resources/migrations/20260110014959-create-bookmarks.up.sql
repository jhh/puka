CREATE TABLE public.bookmark (
    id SERIAL PRIMARY KEY,
    created timestamptz NOT NULL,
    modified timestamptz NOT NULL,
    title varchar(120) NOT NULL,
    description text NOT NULL,
    url varchar(500) NOT NULL,
    title_description_search tsvector,
    active bool NOT NULL
);
--;;
CREATE UNIQUE INDEX bookmark_url_uniq ON public.bookmark USING btree (url);
--;;
CREATE INDEX bookmark_b_created_idx ON public.bookmark USING btree (created DESC);
--;;
CREATE INDEX bookmark_b_title_d_gin ON public.bookmark USING gin (title_description_search);
--;;
CREATE INDEX bookmark_bookmark_url_like ON public.bookmark USING btree (url varchar_pattern_ops);
--;;
CREATE INDEX idx_bookmark_active_created ON public.bookmark USING btree (active, created DESC);
--;;
CREATE TABLE public.tag (
    id SERIAL PRIMARY KEY,
    name varchar(100) NOT NULL,
    slug varchar(100) NOT NULL
);
--;;
CREATE UNIQUE INDEX tag_name_key ON public.tag USING btree (name);
--;;
CREATE UNIQUE INDEX tag_slug_key ON public.tag USING btree (slug);
--;;
CREATE INDEX tag_name_like ON public.tag USING btree (name varchar_pattern_ops);
--;;
CREATE INDEX tag_slug_like ON public.tag USING btree (slug varchar_pattern_ops);
--;;
CREATE TABLE tagging (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER REFERENCES tag(id) ON DELETE CASCADE,
    taggable_type VARCHAR(50) NOT NULL,  -- 'bookmark', 'item', etc.
    taggable_id INTEGER NOT NULL,        -- ID of the tagged entity
    UNIQUE(tag_id, taggable_type, taggable_id)
);
--;;
CREATE INDEX idx_tagging_tag_id ON tagging(tag_id);
--;;
CREATE INDEX idx_tagging_taggable ON tagging(taggable_type, taggable_id);
--;;
CREATE INDEX idx_tagging_type_tag ON tagging(taggable_type, tag_id);
