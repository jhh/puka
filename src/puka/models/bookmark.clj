(ns puka.models.bookmark
  (:require
   [next.jdbc :as jdbc]
   [next.jdbc.sql :as sql]
   [next.jdbc.result-set :as rs]
   [clojure.data.json :as json])
  (:import [org.postgresql.util PGobject]))

(def <-json #(json/read-str % :key-fn keyword))

(<-json "{\"name\": \"Alice\", \"age\": 30}")

(defn <-pgobject
  "Transform PGobject containing `json` or `jsonb` value to Clojure data."
  [^PGobject v]
  (let [type  (.getType v)
        value (.getValue v)]
    (if (#{"jsonb" "json"} type)
      (some-> value <-json (with-meta {:pgtype type}))
      value)))

(extend-protocol rs/ReadableColumn
  org.postgresql.util.PGobject
  (read-column-by-label [^org.postgresql.util.PGobject v _]
    (<-pgobject v))
  (read-column-by-index [^org.postgresql.util.PGobject v _2 _3]
    (<-pgobject v)))

(defn get-bookmarks
  [db opts]
  (sql/find-by-keys (db) :bookmark
                    (if (contains? opts :active)
                      (select-keys opts [:active])
                      :all)
                    (merge {:order-by [:created]} opts)))

(defn get-bookmarks'
  [db opts]
  (sql/query (db) ["
SELECT 
    b.id,
    b.title,
    b.url,
    b.description,
    b.created,
    b.active,
    -- Complete tag objects as JSON array
    COALESCE(
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'id', t.id,
                'name', t.name,
                'slug', t.slug
            ) ORDER BY t.name
        ) FILTER (WHERE t.id IS NOT NULL), 
        '[]'::json
    ) AS tags
FROM bookmark b
LEFT JOIN tagging ti ON ti.taggable_id = b.id
LEFT JOIN tag t ON t.id = ti.tag_id
WHERE b.active = ?
GROUP BY b.id, b.title, b.url, b.description, b.created, b.modified
ORDER BY b.created DESC
OFFSET ?
LIMIT ?;
" (get opts :active true) (get opts :offset 0) (get opts :limit 25)]
             {:builder-fn rs/as-unqualified-maps}))

(comment
  (defn db [] (jdbc/get-datasource {:dbtype "postgresql" :dbname "puka-test"}))
  (time (get-bookmarks db {:active true :offset 0 :limit 25}))
  (time (get-bookmarks' db {:offset 0 :limit 25}))
  (time (jdbc/execute! (db) ["select * from bookmark limit 3"]))

  ;; Benchmark: run get-bookmarks 10 times and average (with paging)
  (let [iterations 20
        times (doall
               (for [i (range iterations)]
                 (let [start (System/nanoTime)
                       _ (doall (get-bookmarks' db {:active true :offset (* i 25) :limit 25}))
                       end (System/nanoTime)]
                   (/ (- end start) 1000000.0))))
        avg (/ (reduce + times) iterations)]
    (println "Times (ms):" times)
    (println "Average:" avg "ms"))
  ;
  )

