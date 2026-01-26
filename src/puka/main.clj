(ns puka.main
  (:require
   [com.stuartsierra.component :as component]
   [puka.controllers.core :as controller]
   [puka.controllers.bookmark :as bookmark]
   [puka.models.core :refer [database-component]]
   [reitit.ring :as ring]
   [reitit.ring.middleware.parameters :as parameters]
   [reitit.ring.coercion :as coercion]
   [reitit.coercion.malli :as malli]
   [ring.adapter.jetty :refer [run-jetty]]
   [ring.util.response :as resp])
  (:gen-class))

(defrecord Application [config    ; config
                        database  ; dependency
                        state]    ; state
  component/Lifecycle
  (start [this]
    (assoc this :state "Running"))
  (stop [this]
    (assoc this :state "Stopped")))

(defn application-component
  [config]
  (component/using (map->Application {:config config})
                   [:database]))

(defn wrap-render-page
  [handler]
  (fn [request]
    (let [resp (handler request)]
      (if (resp/response? resp)
        resp
        (#'controller/render-page resp)))))

(defn wrap-application
  [handler application]
  (fn [request]
    (handler (assoc request :application/component application))))

(defn application-handler [application]
  (ring/ring-handler
   (ring/router
    [["/"           #'controller/default]
     ["/bookmarks/" {:get {:parameters {:query [:map
                                                [:tag {:optional true} :string]
                                                [:page {:optional true} :int]]}}
                     :handler #'bookmark/default}]
     ["/foo/" {:get {:handler #'bookmark/default}}]
     ["/assets/*"   (ring/create-resource-handler)]]
    {:data {:coercion malli/coercion
            :middleware [parameters/parameters-middleware
                         coercion/coerce-request-middleware
                         [wrap-render-page]
                         [wrap-application application]]}})
   (ring/routes
    (ring/create-default-handler
     {:not-found (constantly {:status 404 :body "Not found"})}))))

(defrecord WebServer [handler-fn port         ; parameters
                      application             ; dependencies
                      http-server shutdown]   ; state
  component/Lifecycle
  (start [this]
    (if http-server
      this
      (assoc this
             :http-server (run-jetty (handler-fn application)
                                     {:port port :join? false})
             :shutdown (promise))))

  (stop [this]
    (if http-server
      (do
        (.stop http-server)
        (deliver shutdown true)
        (assoc this :http-server nil))
      this)))

(defn web-server-component
  [handler-fn port]
  (component/using (map->WebServer {:handler-fn handler-fn :port port})
                   [:application]))

(defn new-system
  ([port] (new-system port true))
  ([port repl]
   (component/system-map :application (application-component {:repl repl})
                         :database (database-component)
                         :web-server (web-server-component #'application-handler port))))

(defn -main
  [& [port]]
  (let [port (or port (get (System/getenv) "PORT" 8080))
        port (cond-> port (string? port) Integer/parseInt)]
    (println (format "Listening on http://localhost:%d" port))
    (-> (component/start (new-system port false))
        :web-server :shutdown deref))) ; wait "forever" on the promise created:

(comment
  ;; run the server in the REPL
  (def system (new-system 8888))
  (alter-var-root #'system component/start)
  (alter-var-root #'system component/stop)
  ;;
  ;; use Portal
  (require '[portal.api :as p])
  (def p (p/open))
  (add-tap #'p/submit)
  ;;
  (require '[reitit.core :as r])
  (def app (application-handler (-> system :application)))
  (tap> (r/match-by-path (-> app (ring/get-router)) "/bookmarks/"))
  (app {:request-method :get, :uri "/bookmarks/" :query-string "tag=clojure&page=3"})
  (app {:request-method :get, :uri "/foo/"})
  ;;
  )

