import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import logo from '../assets/safer-logo.png'

export default function Registrar() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [nome, setNome] = useState('')
  const [cpf, setCpf] = useState('')
  const [senha, setSenha] = useState('')
  const [isFunc, setIsFunc] = useState(false)
  const [erro, setErro] = useState('')

  const submit = (e) => {
    e.preventDefault(); setErro('')
    const r = register({ nome, cpf: cpf.replace(/\D/g, ''), senha, isFuncionario: isFunc })
    if (!r.ok) return setErro(r.error)
    navigate('/')
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <div className="auth-logo">
          <img src={logo} alt="SAFER" />
          <h2 style={{ fontSize: '1rem', textTransform: 'none', letterSpacing: 0 }}>Criar conta</h2>
        </div>
        <form onSubmit={submit}>
          <div className="field"><label>Nome completo</label>
            <input className="input" required value={nome} onChange={e => setNome(e.target.value)} /></div>
          <div className="field"><label>CPF</label>
            <input className="input" required placeholder="000.000.000-00" value={cpf} onChange={(e) => {
              const valor = e.target.value
                .replace(/\D/g, '')
                .slice(0, 11)

              setCpf(valor)
            }} /></div>
          <div className="field"><label>Senha</label>
            <input className="input" type="password" required value={senha} onChange={e => setSenha(e.target.value)} /></div>
          <div className="field-row" style={{ marginBottom: '1rem' }}>
            <div>
              <label style={{ margin: 0 }}>Sou funcionário</label>
              <div className="muted" style={{ fontSize: '.72rem' }}>Acesso ao painel de estatísticas.</div>
            </div>
            <button type="button" className={`switch ${isFunc ? 'on' : ''}`} onClick={() => setIsFunc(!isFunc)} />
          </div>
          {erro && <div style={{ color: 'var(--accent)', marginBottom: '.75rem', fontSize: '.8rem' }}>{erro}</div>}
          <button type="submit" className="btn btn-primary btn-block">Cadastrar</button>
          <div className="auth-links" style={{ justifyContent: 'center' }}>
            <Link to="/login">Já tenho conta</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
