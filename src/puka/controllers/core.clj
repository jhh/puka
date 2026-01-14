(ns puka.controllers.core
  (:require [ring.util.response :as resp]
            [puka.layouts.core :as layout]))

(defn render-page
  [request]
  (-> request
      layout/render-view
      str
      resp/response
      (resp/content-type "text/html")))

(defn default
  [request]
  #_(assoc-in request [:params :message] "Hello, Jeffrey!")
  (assoc-in request [:params :content] #html [:p [:span {:class "text-red-600"} "Hello, Jeffrey!"]]))

;; TODO:
;; - redirect from default to bookmarks list
;; - create bookmarks list controller and layout
