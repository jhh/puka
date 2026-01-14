(ns puka.layouts.core
  (:require [borkdude.html :refer [html]]))

(defn base-layout
  [{:keys [title content]
    :or {title ""
         content #html [:p [:strong "No content available!"]]}}]
  (html [:<>
         [:$ "<!DOCTYPE html>"]
         [:html {:lang "en"}
          [:head
           [:meta {:charset "utf-8"}]
           [:title title]]
          [:body
           [:main
            (if (string? content)
              #html [:p content]
              content)]]]]))

(def request->title
  {"/" "Puka"})

(defmulti render-view :application/view)

(defmethod render-view :default
  [{:keys [params] :as request}]
  (let [content (or (:content params)
                    (:message params))
        page (merge {:title (request->title (:uri request "TODO: title"))}
                    (when content {:content content}))]
    (base-layout page)))

(comment
  (str (base-layout {:title "Foo" :content "Bar"}))
  (str (base-layout {:title "Foo" :content #html [:span "Baz"]}))
  (str #html [:div "Hello"])
  ;
  )


