import { Routes, Route, Link, NavLink, useNavigate, Navigate } from 'react-router-dom'
import logo from './assets/safer-logo.png'
import { useAuth } from './context/AuthContext.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Registrar from './pages/Registrar.jsx'
import EsqueciSenha from './pages/EsqueciSenha.jsx'
import Cadastro from './pages/Cadastro.jsx'
import Estatisticas from './pages/Estatisticas.jsx'

function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <header className="topbar">
      <Link to="/" className="brand"><img src={logo} alt="SAFER" /></Link>
      <nav className="nav">
       <NavLink to="/" className="nav-link"> Monitoramento</NavLink>
        {user?.isFuncionario && <NavLink to="/estatisticas" className="nav-link">Estatísticas</NavLink>}
        {user ? (
          <button className="nav-link" onClick={() => { logout(); navigate('/') }}>Sair</button>
        ) : (
          <>
            <NavLink to="/login" className="nav-link">Login</NavLink>
            <NavLink to="/registrar" className="nav-link primary">Cadastrar-se</NavLink>
          </>
        )}
      </nav>
    </header>
  )
}

function RequireAuth({ children, employeeOnly }) {
  const { user, ready } = useAuth()
  if (!ready) return null
  if (!user) return <Navigate to="/login" replace />
  if (employeeOnly && !user.isFuncionario) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <div className="app">
      <Nav />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registrar" element={<Registrar />} />
          <Route path="/esqueci-senha" element={<EsqueciSenha />} />
          <Route path="/cadastro" element={<RequireAuth><Cadastro /></RequireAuth>} />
          <Route path="/estatisticas" element={<RequireAuth employeeOnly><Estatisticas /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/cadastro/:id" element={<Cadastro />} />
        </Routes>
      </main>
    </div>
  )
}
