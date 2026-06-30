import api from "./api";
import type { LoginRequest, RegisterRequest, LoginResponse, User } from "../types";

export const authApi = {
  login: (data: LoginRequest) =>
    api.post("/auth/login", data) as Promise<{ code: number; message: string; data: LoginResponse }>,

  register: (data: RegisterRequest) =>
    api.post("/auth/register", data) as Promise<{ code: number; message: string; data: LoginResponse }>,

  me: () =>
    api.get("/auth/me") as Promise<{ code: number; message: string; data: User }>,
};
