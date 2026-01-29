(ns puka.layouts.bookmark.list-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.layouts.bookmark.list :as sut]))

(defn- ->html [data]
  (sut/partial->html (sut/->partial data)))

(deftest tag-test
  (testing "renders a tag list item with correct links and name"
    (let [sample-tag {:name "Clojure" :slug "clojure"}
          result (str (sut/tag->html sample-tag))]
      (is (re-find #"href=\"\?tag=clojure\"" result))
      (is (re-find #"hx-get=\"\?tag=clojure\"" result))
      (is (re-find #">Clojure</a>" result)))))

(deftest bookmark->html-test
  (testing "renders a bookmark with correct fields"
    (let [bm {:id 123
              :title "My Title"
              :description "My Description"
              :url "https://example.com"
              :created #inst "2026-01-14T12:00:00Z"
              :active false
              :tags [{:name "tag1" :slug "tag1"}]}
          result (str (sut/bookmark->html bm))]
      (is (re-find #"href=\"https://example.com\"" result))
      (is (re-find #"My Title" result))
      (is (re-find #"My Description" result))
      (is (re-find #"\(inactive\)" result))
      (is (re-find #"january 2026" result))
      (is (re-find #"hx-get=\"/bookmarks/123/edit/\"" result))
      (is (re-find #">tag1</a>" result)))))

(deftest html-test
  (testing "renders bookmarks list without HTMX when has-more? is false"
    (let [data {:bookmarks [{:id 1
                             :title "Title 1"
                             :description "Desc 1"
                             :url "https://example.com/1"
                             :created #inst "2026-01-14T12:00:00Z"
                             :active true
                             :tags []}
                            {:id 2
                             :title "Title 2"
                             :description "Desc 2"
                             :url "https://example.com/2"
                             :created #inst "2026-01-14T12:00:00Z"
                             :active true
                             :tags []}]
                :has-more? false
                :page 0}
          result (str (->html data))]
      (is (re-find #"<ul" result))
      (is (re-find #"Title 1" result))
      (is (re-find #"Title 2" result))
      (is (not (re-find #"hx-trigger=\"revealed\"" result))
          "Should not have HTMX attributes when has-more? is false")))

  (testing "renders bookmarks with HTMX on last li when has-more? is true"
    (let [data {:bookmarks [{:id 1
                             :title "Title 1"
                             :description "Desc 1"
                             :url "https://example.com/1"
                             :created #inst "2026-01-14T12:00:00Z"
                             :active true
                             :tags []}
                            {:id 2
                             :title "Title 2"
                             :description "Desc 2"
                             :url "https://example.com/2"
                             :created #inst "2026-01-14T12:00:00Z"
                             :active true
                             :tags []}]
                :has-more? true
                :page 0}
          result (str (->html data))]
      (is (re-find #"Title 1" result))
      (is (re-find #"Title 2" result))
      (is (re-find #"hx-get=\"\?page=1\"" result)
          "Should have next page URL")
      (is (re-find #"hx-trigger=\"revealed\"" result)
          "Should have revealed trigger")
      (is (re-find #"hx-swap=\"outerHTML\"" result)
          "Should have outerHTML swap")))

  (testing "calculates correct next page number"
    (let [data {:bookmarks [{:id 1
                             :title "Title"
                             :description "Desc"
                             :url "https://example.com"
                             :created #inst "2026-01-14T12:00:00Z"
                             :active true
                             :tags []}]
                :has-more? true
                :page 3}
          result (str (->html data))]
      (is (re-find #"hx-get=\"\?page=4\"" result)
          "Should increment page number correctly")))

  (testing "handles empty bookmarks list"
    (let [data {:bookmarks []
                :has-more? false
                :page 0}
          result (str (->html data))]
      (is (re-find #"<ul" result))
      (is (not (re-find #"hx-trigger" result))))))

