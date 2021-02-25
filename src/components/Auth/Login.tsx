import { gql, useMutation } from "@apollo/client";
import { isLoggedInVar } from "../../cache";
import { TokenAuth, TokenAuthVariables } from "../../generated/TokenAuth";
import Error from "../Shared/Error";
import Loading from "../Shared/Loading";
import LoginForm from "./LoginForm";

const Login = () => {
  const [login, { loading, error }] = useMutation<
    TokenAuth,
    TokenAuthVariables
  >(LOGIN_MUTATION, {
    onCompleted({ tokenAuth }) {
      const token = tokenAuth?.token;
      if (token) {
        localStorage.setItem("token", token);
        isLoggedInVar(true);
      }
    },
  });

  if (loading) return <Loading />;
  if (error) return <Error error={error} />;

  return <LoginForm login={login} />;
};

export default Login;

const LOGIN_MUTATION = gql`
  mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;
