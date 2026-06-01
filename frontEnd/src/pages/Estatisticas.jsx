import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import {
  faTrash,
  faPen,
  faPlus
} from '@fortawesome/free-solid-svg-icons'

export default function Estatisticas() {
  const navigate = useNavigate()
  const [pessoas, setPessoas] = useState([])

  useEffect(() => {
    carregarPessoas()
  }, [])

  const carregarPessoas = () => {
    try {
      setPessoas(
        JSON.parse(localStorage.getItem('safer-pessoas')) || []
      )
    } catch {
      setPessoas([])
    }
  }

  const excluirPessoa = (id) => {
    const confirmar = window.confirm(
      'Deseja realmente excluir esta pessoa?'
    )

    if (!confirmar) return

    const novaLista = pessoas.filter(
      pessoa => pessoa.id !== id
    )

    setPessoas(novaLista)

    localStorage.setItem(
      'safer-pessoas',
      JSON.stringify(novaLista)
    )
  }

  const editarPessoa = (id) => {
    navigate(`/cadastro/${id}`)
  }

  const adicionarPessoa = () => {
    navigate('/cadastro')
  }

  const stats = useMemo(() => ({
    total: pessoas.length,
    procurados: pessoas.filter(
      p => p.status === 'Procurado'
    ).length,

    suspeitos: pessoas.filter(
      p => p.status === 'Suspeito'
    ).length,

    monitorados: pessoas.filter(
      p => p.status === 'Monitorado'
    ).length,

    funcionarios: pessoas.filter(
      p => p.isFuncionario
    ).length

  }), [pessoas])

  const max = Math.max(
    stats.procurados,
    stats.suspeitos,
    stats.monitorados,
    1
  )

  const Stat = ({ icon, label, val, tone }) => (
    <div className="card stat-card">
      <div
        className="icon"
        style={{
          background: `${tone}22`,
          color: tone
        }}
      >
        {icon}
      </div>

      <div className="val">{val}</div>

      <div className="lbl">{label}</div>
    </div>
  )

  const Bar = ({ label, value, color }) => (
    <div className="bar-row">
      <div className="bar-head">
        <span>{label}</span>

        <span
          style={{
            fontFamily:
              'ui-monospace, monospace'
          }}
        >
          {value}
        </span>
      </div>

      <div className="bar-bg">
        <div
          className="bar-fill"
          style={{
            width: `${(value / max) * 100}%`,
            background: color
          }}
        />
      </div>
    </div>
  )

  return (
    <section className="container">

      <button
        className="btn btn-ghost"
        onClick={() => navigate('/')}
        style={{ marginBottom: '.5rem' }}
      >
        ← Voltar
      </button>

      <div className="stats-header">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}
        >
          <div className="stats-icon">
            📊
          </div>

          <div>
            <h1 style={{ margin: 0 }}>
              Dashboard
            </h1>

            <p
              className="muted"
              style={{ margin: 0 }}
            >
              Visão geral da base biométrica.
            </p>
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={adicionarPessoa}
        >
          <FontAwesomeIcon
            icon={faPlus}
            style={{
              marginRight: '8px'
            }}
          />

          Adicionar Pessoa
        </button>
      </div>

      <div className="grid-cards">
        <Stat
          icon="👥"
          label="Total cadastrado"
          val={stats.total}
          tone="#3b82f6"
        />

        <Stat
          icon="⚠"
          label="Procurados"
          val={stats.procurados}
          tone="#ef4444"
        />

        <Stat
          icon="🔍"
          label="Suspeitos"
          val={stats.suspeitos}
          tone="#f59e0b"
        />

        <Stat
          icon="🛡"
          label="Funcionários"
          val={stats.funcionarios}
          tone="#10b981"
        />
      </div>

      <div className="card">
        <h2>Distribuição por status</h2>

        <div style={{ marginTop: '1rem' }}>
          <Bar
            label="Procurados"
            value={stats.procurados}
            color="var(--accent)"
          />

          <Bar
            label="Suspeitos"
            value={stats.suspeitos}
            color="var(--warning)"
          />

          <Bar
            label="Monitorados"
            value={stats.monitorados}
            color="var(--primary)"
          />
        </div>
      </div>

      <div
        className="card"
        style={{ marginTop: '1.25rem' }}
      >
        <div
          className="row"
          style={{ marginBottom: 0 }}
        >
          <h2>Últimos cadastros</h2>

          <span className="badge badge-primary">
            {pessoas.length}
          </span>
        </div>

        {pessoas.length === 0 ? (
          <p
            className="muted"
            style={{ marginTop: '1rem' }}
          >
            Nenhum cadastro ainda.
          </p>
        ) : (
          <ul className="lista">
            {pessoas.map((pessoa) => (
              <li
                key={pessoa.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
                <div className="ava">
                  {pessoa.foto ? (
                    <img
                      src={pessoa.foto}
                      alt=""
                    />
                  ) : (
                    '👤'
                  )}
                </div>

                <div
                  className="info"
                  style={{
                    flex: 1
                  }}
                >
                  <div className="nm">
                    {pessoa.nome}
                  </div>

                  <div className="cp">
                    CPF {pessoa.cpf || '—'}
                  </div>
                </div>

                <span className="badge badge-primary">
                  {pessoa.status}
                </span>

                <button
                  className="btn-icon editar"
                  onClick={() =>
                    editarPessoa(
                      pessoa.id
                    )
                  }
                  title="Editar"
                >
                  <FontAwesomeIcon
                    icon={faPen}
                  />
                </button>

                <button
                  className="btn-icon excluir"
                  onClick={() =>
                    excluirPessoa(
                      pessoa.id
                    )
                  }
                  title="Excluir"
                >
                  <FontAwesomeIcon
                    icon={faTrash}
                  />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}