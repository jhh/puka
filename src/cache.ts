import { InMemoryCache, makeVar } from "@apollo/client";
import { relayStylePagination } from "@apollo/client/utilities";

export const cache = new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          allBookmarks: relayStylePagination(["search", "tags" ,"year"]),
          isLoggedIn: {
            read() {
              return isLoggedInVar();
            },
          },
        },
      },
    },
  });
  
  export const isLoggedInVar = makeVar<boolean>(!!localStorage.getItem("token"));