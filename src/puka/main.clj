(ns puka.main
  (:require [reitit.ring :as ring]
            [ring.adapter.jetty :as jetty])
  (:gen-class))

(def app
  (ring/ring-handler
   (ring/router
    ["/" {:get {:handler (fn [_]
                           {:status 200
                            :headers {"Content-Type" "text/plain"}
                            :body "Hello, World"})}}])
   (ring/create-default-handler
    {:not-found (constantly {:status 404 :body "Not found"})})))

(defn -main [& _args]
  (println "Server starting on http://localhost:3000")
  (jetty/run-jetty app {:port 3000 :join? false}))
