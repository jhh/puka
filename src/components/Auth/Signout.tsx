import Button from "@material-ui/core/Button";
import { isLoggedInVar } from "../../cache";

function handleSubmit() {
  localStorage.removeItem("token");
  isLoggedInVar(false);
}

const Login = () => {
  return (
    <Button color="inherit" onClick={() => handleSubmit()}>
      Sign Out
    </Button>
  );
};

export default Login;
