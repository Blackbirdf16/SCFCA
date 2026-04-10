import { http } from "./http";
import { Role, User } from "../types";

interface LoginInput {
  username: string;
  password: string;
}

export const authService = {
  async login(input: LoginInput): Promise<User> {
    const response = await http.post("/api/v1/auth/login", {
      username: input.username,
      password: input.password
    });

    const payload = response.data ?? {};
    return {
      username: payload.username ?? input.username,
      role: (payload.role as Role) ?? "regular"
    };
  },
  async me(): Promise<User> {
    const response = await http.get("/api/v1/auth/me");
    const payload = response.data ?? {};
    return {
      username: payload.username,
      role: payload.role
    } as User;
  },

  async logout(): Promise<void> {
    await http.post("/api/v1/auth/logout");
  }
};