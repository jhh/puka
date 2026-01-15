(ns puka.layouts.bookmark.list
  (:require [borkdude.html :refer [html]]
            [clojure.string :as string])
  (:import [java.time ZoneId]
           [java.time.format DateTimeFormatter]
           [java.util Locale]))

(def ^:private date-formatter
  (DateTimeFormatter/ofPattern "MMMM yyyy" Locale/ENGLISH))

(defn- format-inst
  [inst]
  (string/lower-case
   (.format date-formatter
            (.atZone (.toInstant inst) (ZoneId/systemDefault)))))

(defn tag->html
  [{:keys [name slug]}]
  (let [uri (str "?tags=" slug)
        href {:href uri :hx-get uri}]
    (html [:li {:class "inline text-sm text-red-700 mr-1"}
           [:a {:hx-target "#id_content" :& href} name]])))

(defn bookmark->html
  [{:keys [id title description url created active tags]}]
  (let [link-attr {:href url}
        button-attr {:hx-get (str "/bookmarks/" id "/edit/")}]
    (html [:li {:class "p-4"}
           [:article
            [:h2 {:class "pb-2 text-base font-medium text-slate-800"}
             [:a {:target "_blank", :rel "noreferrer" :& link-attr} title]
             (when-not active
               #html [:span {:class "text-sm text-red-700"} "(inactive)"])]
            [:p {:class "text-sm text-slate-600"} description]
            [:ul {:role "list", :class "mt-4"}
             (html (map tag->html tags))]
            [:div {:class "text-xs text-slate-400"}
             (format-inst created)
             [:button {:type "button"
                       :class "ml-3"
                       :hx-target "#id_content"
                       :hx-push-url "true"
                       :& button-attr} "edit"]]]])))

(defn ->html
  [bookmarks]
  (html [:ul#id_bookmarks {:role list :class "divide-y divide-gray-200 shadow-sm bg-white"}
         (map bookmark->html bookmarks)]))

(comment
  (str (tag->html {:id 1 :name "Foo" :slug "foo"}))

  (def bm
    {:id 3960,
     :title "Awesome",
     :url "https://github.com/sindresorhus/awesome",
     :description
     "😎 Awesome lists about all kinds of interesting topics. Awesome number of stars.",
     :created #inst "2024-12-25T21:27:52.359000000-00:00",
     :active false,
     :tags [{:id 234, :name "github", :slug "github"}]})

  (str (bookmark->html bm))
  ;
  )
