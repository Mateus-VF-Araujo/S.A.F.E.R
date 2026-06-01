import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ScanFace, Radar, BarChart3 } from 'lucide-react'


export default function Cadastro() {
  const navigate = useNavigate()
  const [preview, setPreview] = useState(null)
  const [nome, setNome] = useState('')
  const [cpf, setCpf] = useState('')
  const [status, setStatus] = useState('Monitorado')
  const [isFunc, setIsFunc] = useState(false)

  const onFile = (e) => {
    const f = e.target.files?.[0]; if (!f) return
    const r = new FileReader()
    r.onload = () => setPreview(r.result)
    r.readAsDataURL(f)
  }

  const submit = (e) => {
    e.preventDefault()
    const nova = { id: crypto.randomUUID(), nome, cpf, status, isFuncionario: isFunc, foto: preview }
    let list = []
    try { list = JSON.parse(localStorage.getItem('safer-pessoas')) || [] } catch {}
    localStorage.setItem('safer-pessoas', JSON.stringify([nova, ...list]))
    navigate('/')
  }

  return (
    <section className="container" style={{ maxWidth: 640 }}>
      <h1>Cadastrar pessoa</h1>
      <p className="muted">Adicione um novo registro à base biométrica.</p>

      <div className="card" style={{ marginTop: '1.25rem' }}>
        <form onSubmit={submit}>
          <label>Foto</label>
          <div className="upload-row">
            <div className="avatar">
              {preview ? <img src={preview} alt="" /> : <ScanFace size={34} />}
            </div>
            <label className="upload-btn">
              ⬆ Upload de foto
              <input type="file" accept="image/*" onChange={onFile} />
            </label>
          </div>

          <div className="field"><label>Nome completo</label>
            <input className="input" required value={nome} onChange={e => setNome(e.target.value)} /></div>
          <div className="field"><label>CPF</label>
            <input className="input" required placeholder="000.000.000-00" value={cpf} onChange={(e) => {
              const valor = e.target.value
                .replace(/\D/g, '') // só números
                .slice(0, 11) // máximo 11 dígitos

              setCpf(valor)
            }} /></div>
          <div className="field"><label>Status</label>
            <select className="input" value={status} onChange={e => setStatus(e.target.value)}>
              <option>Procurado</option><option>Suspeito</option><option>Monitorado</option>
            </select></div>

          <div className="field-row" style={{ marginBottom: '1.25rem' }}>
            <div>
              <label style={{ margin: 0 }}>Funcionário</label>
              <div className="muted" style={{ fontSize: '.72rem' }}>Pessoa faz parte da equipe.</div>
            </div>
            <button type="button" className={`switch ${isFunc ? 'on' : ''}`} onClick={() => setIsFunc(!isFunc)} />
          </div>

          <div className="btn-row">
            <button type="button" className="btn" onClick={() => navigate('/')}>Voltar</button>
            <button type="submit" className="btn btn-primary">Cadastrar</button>
          </div>
        </form>
      </div>
    </section>
  )
}
