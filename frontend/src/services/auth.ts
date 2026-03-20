import { http } from "./http";
import { Role, User } from "../types";

interface LoginInput {
  username: string;
  password: string;
  role: Role;
}

export const authService = {
  async login(input: LoginInput): Promise<User> {
    const response = await http.post("/api/v1/auth/login", {
      username: input.username,
      password: input.password,
      role: input.role
    });

    const payload = response.data ?? {};
    return {
      username: payload.username ?? input.username,
      role: payload.role ?? input.role,
      token: payload.token ?? "demo-token"
    };
  }
};