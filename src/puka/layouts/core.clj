(ns puka.layouts.core
  (:require [puka.layouts.base :as base]
            [puka.layouts.bookmark.list :as bookmark.list]))

(def request->title
  {"/" "Puka"
   "/bookmarks/" "Bookmarks"})

(defmulti render-view :application/view)

(defmethod render-view :default
  [{:keys [params] :as request}]
  (let [content (or (:content params)
                    (:message params))
        page (merge {:title (request->title (:uri request))}
                    (when content {:content content}))]
    (base/layout page)))

(defmethod render-view :bookmark/list
  [{:application/keys [data] :as request}]
  (let [paging? (> (:page data) 0)
        content (bookmark.list/->partial data)
        content (if paging? content (bookmark.list/partial->html content))]
    (if (:htmx? request)
      content
      (base/layout (merge {:title (request->title (:uri request))
                           :content (bookmark.list/partial->html content)})))))

(comment
  (str (base/layout {:title "Foo" :content "Bar"}))
  (str (base/layout {:title "Foo" :content #html [:span "Baz"]}))
  (str #html [:div "Hello"])
  ;
  )

