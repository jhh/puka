(ns puka.models.bookmark
  (:require
   [honey.sql :as hsql]
   [honey.sql.helpers :as h]
   [next.jdbc :as jdbc]
   [next.jdbc.result-set :as rs]
   [clojure.data.json :as json])
  (:import [org.postgresql.util PGobject]))

(def <-json #(json/read-str % :key-fn keyword))

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

(def bookmark-list-query
  {:select [:b/id
            :b/title
            :b/url
            :b/description
            :b/created
            :b/active
            [[:coalesce
              [:filter
               [:json_agg
                [:order-by
                 [:json_build_object
                  [:inline "id"] :t/id
                  [:inline "name"] :t/name
                  [:inline "slug"] :t/slug]
                 :t/name]]
               {:where [:is-not :t/id nil]}]
              [:cast [:inline "[]"] :json]]
             :tags]]
   :from [[:bookmark :b]]
   :left-join [[:tagging :ti] [:= :ti/taggable_id :b/id]
               [:tag :t] [:= :t/id :ti/tag_id]]
   :group-by [:b/id :b/title :b/url :b/description :b/created :b/modified]
   :order-by [[:b/created :desc]]})

(defn get-bookmarks
  [db & {:keys [offset limit active] :or {offset 0 limit 25}}]
  (let [query (-> bookmark-list-query
                  (h/offset offset)
                  (h/limit limit)
                  (cond-> (some? active) (h/where [:= :b/active active])))]
    (jdbc/execute! (db) (hsql/format query) {:builder-fn rs/as-unqualified-maps})))

(comment
  (defn db [] (jdbc/get-datasource {:dbtype "postgresql" :dbname "puka-test"}))
  (get-bookmarks db {:active true :offset 15 :limit 25})

  ;; Benchmark: run get-bookmarks 10 times and average (with paging)
  (let [iterations 20
        times (doall
               (for [i (range iterations)]
                 (let [start (System/nanoTime)
                       _ (doall (get-bookmarks db {:active true :offset (* i 25) :limit 25}))
                       end (System/nanoTime)]
                   (/ (- end start) 1000000.0))))
        avg (/ (reduce + times) iterations)]
    (println "Times (ms):" times)
    (println "Average:" avg "ms"))
  ;
  ; Use the connection pool in the database component
  ; N.B. system must be started first
  (require '[puka.main :as main])
  (def db (-> main/system :application :database))
  ;
  (require '[portal.api :as p])
  (def p (p/open))
  (add-tap #'p/submit)
  (tap> :hello)
  (p/clear)
  ;
  )

