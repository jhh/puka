(ns puka.layouts.bookmark.list-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.layouts.bookmark.list :as sut]))

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

