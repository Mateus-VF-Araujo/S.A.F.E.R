import { createContext, useContext, useEffect, useState } from 'react'

const Ctx = createContext(null)
const USERS_KEY = 'safer-users'
const CURRENT_KEY = 'safer-current-cpf'

const readUsers = () => {
  try { return JSON.parse(localStorage.getItem(USERS_KEY)) || [] } catch { return [] }
}
const writeUsers = (l) => localStorage.setItem(USERS_KEY, JSON.stringify(l))

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let list = readUsers()
    if (list.length === 0) {
      list = [{ cpf: '00000000000', nome: 'Agente SAFER', senha: 'safer123', isFuncionario: true }]
      writeUsers(list)
    }
    const cur = localStorage.getItem(CURRENT_KEY)
    if (cur) setUser(list.find(u => u.cpf === cur) || null)
    setReady(true)
  }, [])

  const login = (cpf, senha) => {
    const f = readUsers().find(u => u.cpf === cpf)
    if (!f) return { ok: false, error: 'CPF não encontrado' }
    if (f.senha !== senha) return { ok: false, error: 'Senha inválida' }
    localStorage.setItem(CURRENT_KEY, f.cpf); setUser(f); return { ok: true }
  }
  const logout = () => { localStorage.removeItem(CURRENT_KEY); setUser(null) }
  const register = (u) => {
    const list = readUsers()
    if (list.some(x => x.cpf === u.cpf)) return { ok: false, error: 'CPF já cadastrado' }
    writeUsers([...list, u]); localStorage.setItem(CURRENT_KEY, u.cpf); setUser(u)
    return { ok: true }
  }
  const resetSenha = (cpf, nova) => {
    const list = readUsers()
    const i = list.findIndex(u => u.cpf === cpf)
    if (i < 0) return { ok: false, error: 'CPF não encontrado' }
    list[i] = { ...list[i], senha: nova }; writeUsers(list); return { ok: true }
  }

  return <Ctx.Provider value={{ user, ready, login, logout, register, resetSenha }}>{children}</Ctx.Provider>
}
export const useAuth = () => useContext(Ctx)
