import { ApolloClient, ApolloProvider, InMemoryCache } from "@apollo/client";

import CssBaseline from "@material-ui/core/CssBaseline";
import Header from "./components/Shared/Header";
import App from "./pages/App";

const client = new ApolloClient({
  uri: "http://localhost:8000/graphql/",
  cache: new InMemoryCache(),
});

// Router will go here if needed
const Root = () => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <Header />
    <App />
  </ApolloProvider>
);

export default Root;
