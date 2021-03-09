import { InMemoryCache, makeVar } from "@apollo/client";
import { offsetLimitPagination } from "@apollo/client/utilities";

export const cache = new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          bookmarks: offsetLimitPagination(["search", "tags"]),
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