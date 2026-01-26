(ns puka.layouts.core
  (:require [puka.layouts.base :as base]
            [puka.layouts.bookmark.list :as bookmark.list]))

(def request->title
  {"/" "Puka"})

(defmulti render-view :application/view)

(defmethod render-view :default
  [{:keys [params] :as request}]
  (let [content (or (:content params)
                    (:message params))
        page (merge {:title (request->title (:uri request "TODO: title"))}
                    (when content {:content content}))]
    (base/layout page)))

(defmethod render-view :bookmark/list
  [{:application/keys [data] :as request}]
  (let [content (bookmark.list/->html data)
        page (merge {:title (request->title (:uri request "TODO: bookmark/list"))}
                    {:content content})]
    (base/layout page)))

(comment
  (str (base/layout {:title "Foo" :content "Bar"}))
  (str (base/layout {:title "Foo" :content #html [:span "Baz"]}))
  (str #html [:div "Hello"])
  ;
  )


