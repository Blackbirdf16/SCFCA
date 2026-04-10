import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes";
import "../styles/tailwind.css";
import { AuthProvider } from "../hooks/useAuth";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
export default App;
