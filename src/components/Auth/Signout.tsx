import { isLoggedInVar } from "../../cache";

function handleSubmit() {
  localStorage.removeItem("token");
  isLoggedInVar(false);
  window.location.reload();
}

const Signout = () => {
  return (
    <li color="inherit" onClick={() => handleSubmit()}>
      Sign Out
    </li>
  );
};

export default Signout;
