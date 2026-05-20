# Histórias de Usuário - S.A.F.E.R

## 1. Monitorar e Identificar Rostos

**Descrição**  
Como operador de um sistema de monitoramento, eu quero que o software compare os rostos captados pelas câmeras com o banco de dados de criminosos procurados, para que eu possa ser alertado imediatamente da presença de um suspeito em uma área vigiada.

**Prioridade:** Alta  
**Estimativa:** Não informada

### Critérios de Aceitação

1. Identificação em tempo real: o sistema deve ser capaz de detectar rostos em fluxos de vídeo ao vivo com um atraso (latência) máximo de X segundos.
2. Qualidade da imagem: o sistema deve descartar automaticamente capturas que não possuam iluminação ou nitidez mínimas necessárias para o processamento.
3. Nível de confiança: o alerta só deve ser disparado se a similaridade entre o rosto captado e o registro no banco for igual ou superior a X% (ex.: 85%).

## 2. Cadastrar Novos Rostos no Banco de Entidades

**Descrição**  
Como administrador da segurança, eu quero cadastrar e atualizar fotos e dados de indivíduos procurados no banco de dados, para que o sistema tenha informações atualizadas para a identificação.

**Prioridade:** Alta  
**Estimativa:** Não informada

### Critérios de Aceitação

1. O administrador deve poder cadastrar novos indivíduos procurados com dados pessoais e foto.
2. O sistema deve permitir o upload de imagem válida (ex.: JPG ou PNG) para o indivíduo.
3. O sistema deve validar campos obrigatórios antes de permitir o cadastro.
4. O administrador deve poder editar os dados de um indivíduo já cadastrado.
5. O administrador deve poder atualizar ou substituir a foto do indivíduo.

## 3. Alerta de Risco para Policiais

**Descrição**  
Como agente de segurança pública ou privada do local, quero ser notificado de forma sonora e possivelmente em algum dispositivo móvel sobre um resultado positivo na identificação de alguém que consta no banco de dados.

**Prioridade:** Alta  
**Estimativa:** Não informada

### Critérios de Aceitação

1. A notificação deve conter informações básicas do indivíduo identificado (ex.: nome e foto).
2. O agente deve conseguir visualizar os detalhes completos ao acessar a notificação.
3. O sistema deve garantir que apenas agentes autorizados recebam as notificações.
4. A notificação deve ocorrer em tempo próximo ao real após a identificação.
5. O sistema deve registrar o histórico das notificações enviadas.
