import CssBaseline from "@material-ui/core/CssBaseline";
import Header from "./components/Shared/Header";
import App from "./pages/App";

// Router will go here if needed
const Root = () => (
  <>
    <CssBaseline />
    <Header />
    <App />
  </>
);

export default Root;
