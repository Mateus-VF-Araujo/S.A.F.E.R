import { useEffect, useRef, useState } from 'react'
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
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const iniciarCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      })

      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (erro) {
      console.error('Erro ao abrir câmera:', erro)

      alert(
        'Não foi possível acessar a câmera. Verifique as permissões do navegador.'
      )
    }
  }

  const identificar = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }

    setEstado({ tipo: 'scanning' })

    let pessoas = []

    try {
      pessoas = JSON.parse(localStorage.getItem('safer-pessoas')) || []
    } catch {
      pessoas = []
    }

    const encontrou = pessoas.length > 0 && Math.random() < 0.7

    timerRef.current = setTimeout(() => {
      if (encontrou) {
        const pessoa =
          pessoas[Math.floor(Math.random() * pessoas.length)]

        setEstado({
          tipo: 'found',
          pessoa,
          confianca: 80 + Math.random() * 19
        })
      } else {
        setEstado({
          tipo: 'not_found'
        })
      }
    }, 5000)
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
      ? {
          label: 'ANALISANDO…',
          cls: 'badge-primary'
        }
      : estado.tipo === 'found'
      ? {
          label: 'IDENTIFICADO',
          cls: 'badge-success'
        }
      : estado.tipo === 'not_found'
      ? {
          label: 'NÃO ENCONTRADO',
          cls: 'badge-danger'
        }
      : {
          label: 'AGUARDANDO',
          cls: 'badge-muted'
        }

  return (
    <section className="container">
      <div className="row">
        <div>
          <span className="badge badge-success">
            <span className="dot" />
            Sistema online
          </span>

          <h1>
            Reconhecimento{' '}
            <span className="gradient-text">
              Facial
            </span>
          </h1>

          <p className="muted">
            Aponte para a câmera e identifique a
            pessoa em tempo real.
          </p>
        </div>

        <span className={`badge ${status.cls}`}>
          {status.label}
        </span>
      </div>

      <div
        className="card"
        style={{ marginTop: '1.25rem' }}
      >
        <div
          className="row"
          style={{ marginBottom: 0 }}
        >
          <h2>📹 Stream ao vivo</h2>

          <span
            className="muted"
            style={{
              fontFamily:
                'ui-monospace, monospace',
              fontSize: '.75rem'
            }}
          >
            {clock}
          </span>
        </div>

        <div className="stream">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-video"
          />

          {estado.tipo === 'scanning' && (
            <div className="scan-line" />
          )}

          {(estado.tipo === 'scanning' ||
            estado.tipo === 'found') && (
            <div
              className={`detect-box ${
                estado.tipo === 'found'
                  ? 'found'
                  : ''
              }`}
            >
              {estado.tipo === 'found' && (
                <span className="tag">
                  {estado.pessoa.nome} ·{' '}
                  {estado.confianca.toFixed(1)}%
                </span>
              )}
            </div>
          )}

          <div className="stream-overlay">
            <span>
              ● REC · 1920×1080
            </span>
            <span>CAM 04</span>
          </div>
        </div>

        <div className="identity">
          <div className="id-box">
            <div className="id-label">
              Identidade
            </div>

            {estado.tipo === 'found' ? (
              <div>
                <div className="id-name">
                  {estado.pessoa.nome}
                </div>

                <div
                  style={{
                    marginTop: '.35rem',
                    display: 'flex',
                    gap: '.5rem',
                    alignItems: 'center'
                  }}
                >
                  <span className="badge badge-warning">
                    {estado.pessoa.status}
                  </span>

                  <span
                    className="muted"
                    style={{
                      fontSize: '.78rem'
                    }}
                  >
                    Confiança{' '}
                    {estado.confianca.toFixed(
                      1
                    )}
                    %
                  </span>
                </div>
              </div>
            ) : estado.tipo === 'scanning' ? (
              <div
                className="muted"
                style={{
                  marginTop: '.35rem'
                }}
              >
                Analisando rosto…
              </div>
            ) : estado.tipo === 'not_found' ? (
              <div
                style={{
                  marginTop: '.35rem',
                  color:
                    'var(--accent)'
                }}
              >
                Pessoa não localizada na base.
              </div>
            ) : (
              <div
                className="muted"
                style={{
                  marginTop: '.35rem'
                }}
              >
                Aguardando identificação.
              </div>
            )}
          </div>

          <button
            onClick={identificar}
            disabled={
              estado.tipo === 'scanning'
            }
            className="btn btn-primary"
          >
            🔍{' '}
            {estado.tipo === 'scanning'
              ? 'Identificando...'
              : 'Identificar rosto'}
          </button>
        </div>

        {estado.tipo === 'not_found' && (
          <div className="alert-box">
            <div>
              <div className="alert-title">
                ⚠ Pessoa não encontrada
              </div>

              <div className="alert-sub">
                Deseja cadastrá-la agora na
                base biométrica?
              </div>
            </div>

            <button
              onClick={cadastrar}
              className="btn btn-danger"
            >
              Cadastrar pessoa
            </button>
          </div>
        )}
      </div>

      {!user && (
        <p
          className="muted"
          style={{
            textAlign: 'center',
            marginTop: '1rem',
            fontSize: '.78rem'
          }}
        >
          Para cadastrar uma pessoa,
          <Link
            to="/login"
            style={{
              color:
                'var(--primary-2)'
            }}
          >
            {' '}
            faça login
          </Link>
          .
        </p>
      )}
    </section>
  )
}