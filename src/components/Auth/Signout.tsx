import MenuItem from "@material-ui/core/MenuItem";
import { isLoggedInVar } from "../../cache";

function handleSubmit() {
  localStorage.removeItem("token");
  isLoggedInVar(false);
  window.location.reload();
}

const Login = () => {
  return (
    <MenuItem color="inherit" onClick={() => handleSubmit()}>
      Sign Out
    </MenuItem>
  );
};

export default Login;
