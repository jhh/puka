import { ApolloClient, gql, InMemoryCache } from "@apollo/client";

const client = new ApolloClient({
  uri: "http://localhost:8000/graphql/",
  cache: new InMemoryCache(),
});

function App() {
  return <div>App</div>;
}

export default App;

const BOOKMARKS_QUERY = gql`
  {
    bookmarks {
      title
      description
      url
      tags
      createdAt
    }
  }
`;

client.query({ query: BOOKMARKS_QUERY }).then((res) => console.log(res));
