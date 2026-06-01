import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function EsqueciSenha() {
  const { resetSenha } = useAuth()
  const navigate = useNavigate()
  const [cpf, setCpf] = useState('')
  const [nova, setNova] = useState('')
  const [erro, setErro] = useState('')

  const submit = (e) => {
    e.preventDefault(); setErro('')
    const r = resetSenha(cpf.replace(/\D/g, ''), nova)
    if (!r.ok) return setErro(r.error)
    navigate('/login')
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <h2 style={{ fontSize: '1.1rem', textTransform: 'none', letterSpacing: 0 }}>Recuperar senha</h2>
        <p className="muted" style={{ marginTop: '.25rem' }}>Informe seu CPF e a nova senha.</p>
        <form onSubmit={submit} style={{ marginTop: '1.25rem' }}>
          <div className="field"><label>CPF</label>
            <input className="input" required value={cpf} onChange={e => setCpf(e.target.value)} /></div>
          <div className="field"><label>Nova senha</label>
            <input className="input" type="password" required value={nova} onChange={e => setNova(e.target.value)} /></div>
          {erro && <div style={{ color: 'var(--accent)', marginBottom: '.75rem', fontSize: '.8rem' }}>{erro}</div>}
          <button type="submit" className="btn btn-primary btn-block">Redefinir senha</button>
          <div className="auth-links" style={{ justifyContent: 'center' }}>
            <Link to="/login">Voltar ao login</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
