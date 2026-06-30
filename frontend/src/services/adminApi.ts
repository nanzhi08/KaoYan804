import api from "./api";
import type { UserWithStats, InviteCode } from "../types";

export const adminApi = {
  fetchUsers: () =>
    api.get("/admin/users") as Promise<{ code: number; message: string; data: UserWithStats[] }>,

  deleteUser: (id: number) =>
    api.delete(`/admin/users/${id}`) as Promise<{ code: number; message: string }>,

  createInviteCode: () =>
    api.post("/admin/invite-codes") as Promise<{ code: number; message: string; data: InviteCode }>,

  fetchInviteCodes: () =>
    api.get("/admin/invite-codes") as Promise<{ code: number; message: string; data: InviteCode[] }>,

  deleteInviteCode: (id: number) =>
    api.delete(`/admin/invite-codes/${id}`) as Promise<{ code: number; message: string }>,
};