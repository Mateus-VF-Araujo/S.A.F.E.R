import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import logo from '../assets/safer-logo.png'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [cpf, setCpf] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')

  const submit = (e) => {
    e.preventDefault(); setErro('')
    const r = login(cpf.replace(/\D/g, ''), senha)
    if (!r.ok) return setErro(r.error)
    navigate('/')
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <div className="auth-logo">
          <img src={logo} alt="SAFER" />
          <span className="muted" style={{ fontSize: '.8rem' }}>Acesso restrito · Identifique-se</span>
        </div>
        <form onSubmit={submit}>
          <div className="field">
            <label>CPF</label>
            <input className="input" inputMode="numeric" required placeholder="000.000.000-00"
              value={cpf} onChange={(e) => {
                const valor = e.target.value
                  .replace(/\D/g, '') // só números
                  .slice(0, 11) // máximo 11 dígitos

                setCpf(valor)
              }}
            />
          </div>
          <div className="field">
            <label>Senha</label>
            <input className="input" type="password" required placeholder="••••••••"
              value={senha} onChange={e => setSenha(e.target.value)} />
          </div>
          {erro && <div className="muted" style={{ color: 'var(--accent)', marginBottom: '.75rem', fontSize: '.8rem' }}>{erro}</div>}
          <button type="submit" className="btn btn-primary btn-block">Entrar</button>
          <div className="auth-links">
            <Link to="/esqueci-senha">Esqueci minha senha</Link>
            <Link to="/registrar">Cadastrar-se</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
