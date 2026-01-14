(ns puka.layouts.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.layouts.base :as sut]
            [borkdude.html :refer [html]]))

(deftest base-layout-defaults-test
  (testing "Default behavior with nil or empty arguments"
    (testing "with nil argument"
      (let [result (str (sut/layout nil))]
        (is (re-find #"<title></title>" result)
            "Should include empty title tag")
        (is (re-find #"<p><strong>No content available!</strong></p>" result)
            "Should include default content")))

    (testing "with empty map"
      (let [result (str (sut/layout {}))]
        (is (re-find #"<p><strong>No content available!</strong></p>" result)
            "Should include default content")))))

(deftest base-layout-title-test
  (testing "Title rendering and escaping"
    (testing "with custom title"
      (let [result (str (sut/layout {:title "My Title"}))]
        (is (re-find #"<title>My Title</title>" result)
            "Should include custom title")))

    (testing "with HTML characters in title (XSS protection)"
      (let [result (str (sut/layout {:title "<script>alert('xss')</script>"}))]
        (is (re-find #"<title>&lt;script&gt;.*&lt;/script&gt;</title>" result)
            "Should escape HTML characters in title")
        (is (not (re-find #"<script>" result))
            "Should not include unescaped script tag")))))

(deftest base-layout-string-content-test
  (testing "String content wrapping and escaping"
    (testing "string content is wrapped in <p> tag"
      (let [result (str (sut/layout {:content "Hello World"}))]
        (is (re-find #"<main><p>Hello World</p></main>" result)
            "Should wrap string content in <p> tag")))

    (testing "string content with HTML characters (escaped)"
      (let [result (str (sut/layout {:content "<b>Bold</b> & <i>Italic</i>"}))]
        (is (re-find #"&lt;b&gt;Bold&lt;/b&gt;" result)
            "Should escape <b> tags")
        (is (re-find #"&amp;" result)
            "Should escape ampersand")
        (is (re-find #"&lt;i&gt;Italic&lt;/i&gt;" result)
            "Should escape <i> tags")
        (is (not (re-find #"<b>" result))
            "Should not include unescaped <b> tag")))

    (testing "empty string content"
      (let [result (str (sut/layout {:content ""}))]
        (is (re-find #"<main><p></p></main>" result)
            "Should include empty <p> tag")))))

(deftest base-layout-html-content-test
  (testing "HTML/hiccup content rendering"
    (testing "HTML content (hiccup vector)"
      (let [result (str (sut/layout {:content (html [:div "Custom"])}))]
        (is (re-find #"<main><div>Custom</div></main>" result)
            "Should render hiccup vector as HTML")))

    (testing "nested HTML content"
      (let [result (str (sut/layout {:content (html [:div [:span "Nested"] [:p "Content"]])}))]
        (is (re-find #"<div><span>Nested</span><p>Content</p></div>" result)
            "Should render nested hiccup structures")))))

(deftest base-layout-combined-test
  (testing "Combined title and content"
    (testing "both title and content specified"
      (let [result (str (sut/layout {:title "Test" :content "Content"}))]
        (is (re-find #"<title>Test</title>" result)
            "Should include custom title")
        (is (re-find #"<main><p>Content</p></main>" result)
            "Should include custom content")))))

(deftest base-layout-structure-test
  (testing "HTML5 document structure"
    (let [result (str (sut/layout nil))]
      (is (re-find #"<!DOCTYPE html>" result)
          "Should start with DOCTYPE")
      (is (re-find #"<html.*?>.*</html>" result)
          "Should have html tags")
      (is (re-find #"<head>.*</head>" result)
          "Should have head section")
      (is (re-find #"<body>.*</body>" result)
          "Should have body section")
      (is (re-find #"<main>.*</main>" result)
          "Should have main section"))))
