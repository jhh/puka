(ns puka.layouts.core
  (:require [borkdude.html :refer [html]]))

(defn base-layout
  [content]
  (html [:<>
         [:$ "<!DOCTYPE html>"]
         [:html {:lang "en"}
          [:head
           [:meta {:charset "utf-8"}]
           [:title content]]
          [:body
           [:main
            [:p content]]]]]))

(defn render-page
  [content]
  {:status 200
   :headers {"Content-Type" "text/html; charset=utf-8"}
   :body (str (base-layout content))})

(comment
  (str (base-layout "HI")))


