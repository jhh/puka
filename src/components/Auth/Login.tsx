import { gql, useMutation } from "@apollo/client";
import { message } from "antd";
import { isLoggedInVar } from "../../cache";
import { TokenAuth, TokenAuthVariables } from "../../generated/TokenAuth";
import LoginForm from "./LoginForm";

const Login = () => {
  const [login, { error }] = useMutation<TokenAuth, TokenAuthVariables>(
    LOGIN_MUTATION,
    {
      onCompleted({ tokenAuth }) {
        const token = tokenAuth?.token;
        if (token) {
          localStorage.setItem("token", token);
          isLoggedInVar(true);
        }
      },
    }
  );

  if (error) message.error(`Login error: ${error.message}`);

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
