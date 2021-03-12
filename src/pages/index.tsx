import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Bookmarks from "./Bookmarks";
import Search from "./Search";

const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Bookmarks />} />
      <Route path="search" element={<Search />} />
    </Routes>
  </Router>
);

export default Root;
