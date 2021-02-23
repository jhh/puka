import { gql, useMutation } from "@apollo/client";
import LoginForm from "./LoginForm";
import { LoginData } from "../Shared/types";
import Loading from "../Shared/Loading";
import Error from "../Shared/Error";
import { isLoggedInVar } from "../../cache";

export type LoginVars = {
  username: string;
  password: string;
};

const Login = () => {
  const [login, { loading, error }] = useMutation<LoginData, LoginVars>(
    LOGIN_MUTATION,
    {
      onCompleted(data) {
        const {
          tokenAuth: { token },
        } = data;
        if (token) {
          console.log(token);
          localStorage.setItem("token", token);
          isLoggedInVar(true);
        }
      },
    }
  );

  if (loading) return <Loading />;
  if (error) return <Error error={error} />;

  return <LoginForm login={login} />;
};

export default Login;

const LOGIN_MUTATION = gql`
  mutation($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;
