import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Home() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [clock, setClock] = useState('--:--:--')
  const [estado, setEstado] = useState({ tipo: 'idle' })

  const timerRef = useRef(null)
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  
  const wsRef = useRef(null)
  const canvasRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    setClock(new Date().toLocaleTimeString('pt-BR'))
    const intervalo = setInterval(() => {
      setClock(new Date().toLocaleTimeString('pt-BR'))
    }, 1000)
    return () => clearInterval(intervalo)
  }, [])

  useEffect(() => {
    iniciarCamera()
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (wsRef.current) wsRef.current.close()
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const iniciarCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (erro) {
      console.error('Erro ao abrir câmera:', erro)
      alert('Não foi possível acessar a câmera. Verifique as permissões do navegador.')
    }
  }

  const conectarWebSocket = useCallback(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/recognition')
    
    wsRef.current.onopen = () => console.log('Conectado ao backend biométrico.')
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.results && data.results.length > 0) {
        const match = data.results[0]
        
        if (match.status === 'unknown') {
          setEstado({ tipo: 'not_found' })
        } else {
          let statusLabel = 'Monitorado'
          if (match.status === 'wanted_alert') statusLabel = 'Procurado'
          if (match.status === 'employee_authorized') statusLabel = 'Funcionário'
          if (match.status === 'common_cleared') statusLabel = 'Liberado'

          setEstado({
            tipo: 'found',
            pessoa: {
              nome: match.full_name,
              status: statusLabel,
              cpf: match.cpf
            },
            confianca: 99.9 
          })
          
          pararIdentificacao()
        }
      }
    }

    wsRef.current.onerror = (error) => {
      console.error("Erro no WebSocket:", error)
      setEstado({ tipo: 'idle' })
    }
  }, [])

  const enviarFrame = () => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    const video = videoRef.current
    const canvas = canvasRef.current
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    const base64Frame = canvas.toDataURL('image/jpeg', 0.7)

    const payload = {
      frame: base64Frame,
      ellipse_center: [canvas.width / 2, canvas.height / 2],
      ellipse_axes: [150, 200]
    }

    wsRef.current.send(JSON.stringify(payload))
  }

  const identificar = () => {
    if (estado.tipo === 'scanning') return
    setEstado({ tipo: 'scanning' })

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      conectarWebSocket()
    }

    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(enviarFrame, 100)
    
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      if (estado.tipo === 'scanning') {
        pararIdentificacao()
        setEstado({ tipo: 'not_found' })
      }
    }, 10000)
  }

  const pararIdentificacao = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)
  }

  const cadastrar = () => {
    if (user) {
      navigate('/cadastro')
    } else {
      navigate('/login')
    }
  }

  const status =
    estado.tipo === 'scanning'
      ? { label: 'ANALISANDO…', cls: 'badge-primary' }
      : estado.tipo === 'found'
      ? { label: 'IDENTIFICADO', cls: 'badge-success' }
      : estado.tipo === 'not_found'
      ? { label: 'NÃO ENCONTRADO', cls: 'badge-danger' }
      : { label: 'AGUARDANDO', cls: 'badge-muted' }

  return (
    <section className="container">
      {/* CANVAS OCULTO PARA EXTRAÇÃO DE FRAMES */}
      <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />

      <div className="row">
        <div>
          <span className="badge badge-success"><span className="dot" />Sistema online</span>
          <h1>Reconhecimento <span className="gradient-text">Facial</span></h1>
          <p className="muted">Aponte para a câmera e identifique a pessoa em tempo real.</p>
        </div>
        <span className={`badge ${status.cls}`}>{status.label}</span>
      </div>

      <div className="card" style={{ marginTop: '1.25rem' }}>
        <div className="row" style={{ marginBottom: 0 }}>
          <h2>📹 Stream ao vivo</h2>
          <span className="muted" style={{ fontFamily: 'ui-monospace, monospace', fontSize: '.75rem' }}>
            {clock}
          </span>
        </div>

        <div className="stream">
          <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
          
          {estado.tipo === 'scanning' && <div className="scan-line" />}
          
          {(estado.tipo === 'scanning' || estado.tipo === 'found') && (
            <div className={`detect-box ${estado.tipo === 'found' ? 'found' : ''}`}>
              {estado.tipo === 'found' && (
                <span className="tag">
                  {estado.pessoa.nome} · {estado.confianca.toFixed(1)}%
                </span>
              )}
            </div>
          )}

          <div className="stream-overlay">
            <span>● REC · 640×480</span>
            <span>CAM 01</span>
          </div>
        </div>

        <div className="identity">
          <div className="id-box">
            <div className="id-label">Identidade</div>
            {estado.tipo === 'found' ? (
              <div>
                <div className="id-name">{estado.pessoa.nome}</div>
                <div style={{ marginTop: '.35rem', display: 'flex', gap: '.5rem', alignItems: 'center' }}>
                  <span className="badge badge-warning">{estado.pessoa.status}</span>
                </div>
              </div>
            ) : estado.tipo === 'scanning' ? (
              <div className="muted" style={{ marginTop: '.35rem' }}>Analisando rosto no backend…</div>
            ) : estado.tipo === 'not_found' ? (
              <div style={{ marginTop: '.35rem', color: 'var(--accent)' }}>Pessoa não localizada na base.</div>
            ) : (
              <div className="muted" style={{ marginTop: '.35rem' }}>Aguardando inicialização da rede neural.</div>
            )}
          </div>

          <button onClick={identificar} disabled={estado.tipo === 'scanning'} className="btn btn-primary">
            🔍 {estado.tipo === 'scanning' ? 'Identificando...' : 'Identificar rosto'}
          </button>
        </div>

        {estado.tipo === 'not_found' && (
          <div className="alert-box">
            <div>
              <div className="alert-title">⚠ Pessoa não encontrada</div>
              <div className="alert-sub">Deseja cadastrá-la agora na base biométrica?</div>
            </div>
            <button onClick={cadastrar} className="btn btn-danger">Cadastrar pessoa</button>
          </div>
        )}
      </div>

      {!user && (
        <p className="muted" style={{ textAlign: 'center', marginTop: '1rem', fontSize: '.78rem' }}>
          Para cadastrar uma pessoa, <Link to="/login" style={{ color: 'var(--primary-2)' }}> faça login</Link>.
        </p>
      )}
    </section>
  )
}