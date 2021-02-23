import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Header from "../components/Shared/Header";
import Home from "./Home";
import Search from "./Search";

// Router will go here if needed
const Root = () => (
  <Router>
    <Header />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="search" element={<Search />} />
    </Routes>
  </Router>
);

export default Root;
