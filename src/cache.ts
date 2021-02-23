import { InMemoryCache, makeVar } from "@apollo/client";

export const cache = new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
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