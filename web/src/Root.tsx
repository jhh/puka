import { ApolloClient, ApolloProvider, InMemoryCache } from "@apollo/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import CssBaseline from "@material-ui/core/CssBaseline";
import Header from "./components/Shared/Header";
import Home from "./pages/Home";
import Search from "./pages/Search";

const client = new ApolloClient({
  uri: "http://localhost:8000/graphql/",
  cache: new InMemoryCache(),
});

// Router will go here if needed
const Root = () => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="search" element={<Search />} />
      </Routes>
    </Router>
  </ApolloProvider>
);

export default Root;
