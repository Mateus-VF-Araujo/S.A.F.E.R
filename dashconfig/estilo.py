fonte_e_grade_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

*:not(.material-symbols-rounded):not(.material-icons):not([data-testid="stIconMaterial"]) {
    font-family: 'Rajdhani', sans-serif !important;
}

.material-symbols-rounded, .material-icons, [data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}

[data-testid="stAppViewContainer"] {
    background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGcgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMDQzMDQ4IiBzdHJva2Utd2lkdGg9IjAuNSI+PHBhdGggZD0iTTAgMGg0MHY0MEgwWiIvPjxwYXRoIGQ9Ik0wIDEwaDQwTTAgMjBoNDBNMCAzMGg0ME0xMCAwaDEwdjQwSDEwWk0yMCAwaDEwdjQwSDIwWiIvPjwvZz48L3N2Zz4=');
    background-repeat: repeat;
}

[data-testid="stMetricValue"] {
    color: #00d6ff;
    text-shadow: 0 0 5px #00d6ff80;
}

/* --- ESTILIZAÇÃO DO LOGIN (PÍLULAS E FORMULÁRIO) --- */

/* Remove a borda padrão do formulário do Streamlit */
div[data-testid="stForm"] {
    border: none !important;
    background-color: transparent !important;
    padding: 0 !important;
}

/* Arredondando e colorindo o container principal do input */
div[data-baseweb="input"] {
    border-radius: 30px !important;
    border: 1px solid #00d6ff50 !important;
    background-color: #031422 !important;
    padding: 3px 10px;
    overflow: hidden !important; /* Corta as pontas quadradas que tentarem vazar */
}

/* Forçando os elementos retangulares de dentro a ficarem invisíveis/transparentes */
div[data-baseweb="input"] > div, 
div[data-baseweb="input"] input {
    background-color: transparent !important;
    color: #ffffff !important; /* Garante que o texto digitado seja branco */
}

/* Efeito de brilho ao clicar dentro do campo */
div[data-baseweb="input"]:focus-within {
    border: 1px solid #00d6ff !important;
    box-shadow: 0 0 10px #00d6ff50 !important;
}

/* Estilizando o botão de submit do formulário */
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 30px;
    background-color: #00d6ff;
    color: #020c15;
    font-size: 1.3rem;
    font-weight: 700;
    border: none;
    padding: 8px;
    box-shadow: 0 0 15px #00d6ff60;
    transition: all 0.3s ease;
    margin-top: 15px;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #ffffff;
    color: #020c15;
    box-shadow: 0 0 25px #00d6ff;
    border: none;
}
</style>
"""

# Cor e imagem
cor_ciano_neon = "#00d6ff"
cor_texto_subtitulo = "#93c9d1"

svg_principal = f'<svg width="100%" height="100%" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" stroke="{cor_ciano_neon}" stroke-width="1.5" fill="none" /><circle cx="50" cy="50" r="30" stroke="{cor_ciano_neon}" stroke-width="1.5" fill="none" /><circle cx="50" cy="50" r="15" stroke="{cor_ciano_neon}" stroke-width="3" fill="none" /><line x1="50" y1="5" x2="50" y2="95" stroke="{cor_ciano_neon}" stroke-width="1.5" /><line x1="5" y1="50" x2="95" y2="50" stroke="{cor_ciano_neon}" stroke-width="1.5" /></svg>'


html_arte_vertical = f"""
<div style="background-color: #020c15; border-radius: 20px; padding: 40px 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 1px solid {cor_ciano_neon}50; box-shadow: 0 0 20px {cor_ciano_neon}10; position: relative; margin-top: 20px;">
<div style="position: absolute; top: 15px; left: 15px; width: 20px; height: 20px; border-top: 2px solid {cor_ciano_neon}; border-left: 2px solid {cor_ciano_neon};"></div>
<div style="position: absolute; top: 15px; right: 15px; width: 20px; height: 20px; border-top: 2px solid {cor_ciano_neon}; border-right: 2px solid {cor_ciano_neon};"></div>
<div style="position: absolute; bottom: 15px; left: 15px; width: 20px; height: 20px; border-bottom: 2px solid {cor_ciano_neon}; border-left: 2px solid {cor_ciano_neon};"></div>
<div style="position: absolute; bottom: 15px; right: 15px; width: 20px; height: 20px; border-bottom: 2px solid {cor_ciano_neon}; border-right: 2px solid {cor_ciano_neon};"></div>
<div style="width: 150px; height: 150px; border: 2px solid {cor_ciano_neon}; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px {cor_ciano_neon}40; padding: 15px; margin-bottom: 25px;">
{svg_principal}
</div>
<h1 style="font-family: 'Rajdhani', sans-serif !important; font-size: 3.5rem; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1; letter-spacing: 2px;">S.A.F.E.R.</h1>
<h2 style="font-family: 'Rajdhani', sans-serif !important; font-size: 1.2rem; font-weight: 400; color: {cor_texto_subtitulo}; margin: 10px 0;">Sistema de Análise Facial para Entidades de Risco</h2>
<div style="width: 40px; height: 2px; background-color: {cor_ciano_neon}; margin: 15px auto;"></div>
<p style="font-family: 'Rajdhani', sans-serif !important; font-size: 0.95rem; color: {cor_texto_subtitulo}; margin: 0;">Terminal de Acesso Restrito.<br>Reconhecimento facial para apoio à identificação de criminosos.</p>
</div>
"""

svg_principal = f'<svg width="100%" height="100%" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" stroke="{cor_ciano_neon}" stroke-width="1.5" fill="none" /><circle cx="50" cy="50" r="30" stroke="{cor_ciano_neon}" stroke-width="1.5" fill="none" /><circle cx="50" cy="50" r="15" stroke="{cor_ciano_neon}" stroke-width="3" fill="none" /><line x1="50" y1="5" x2="50" y2="95" stroke="{cor_ciano_neon}" stroke-width="1.5" /><line x1="5" y1="50" x2="95" y2="50" stroke="{cor_ciano_neon}" stroke-width="1.5" /></svg>'
svg_secundaria = f'<svg width="100%" height="100%" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="{cor_ciano_neon}" stroke-width="2" fill="none" stroke-opacity="0.3" /><line x1="50" y1="20" x2="50" y2="80" stroke="{cor_ciano_neon}" stroke-width="2" stroke-opacity="0.3" /><line x1="20" y1="50" x2="80" y2="50" stroke="{cor_ciano_neon}" stroke-width="2" stroke-opacity="0.3" /></svg>'

html_estrutura = f"""
<div style="background-color: #020c15; border-radius: 10px; padding: 20px; display: flex; align-items: center; justify-content: space-between; background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGcgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMDQzMDQ4IiBzdHJva2Utd2lkdGg9IjAuNSI+PHBhdGggZD0iTTAgMGg0MHY0MEgwWiIvPjxwYXRoIGQ9Ik0wIDEwaDQwTTAgMjBoNDBNMCAzMGg0ME0xMCAwaDEwdjQwSDEwWk0yMCAwaDEwdjQwSDIwWiIvPjwvZz48L3N2Zz4='); border: 1px solid {cor_ciano_neon}30; box-shadow: 0 0 10px {cor_ciano_neon}10; margin-bottom: 30px;">
<div style="display: flex; align-items: center; gap: 30px;">
<div style="width: 150px; height: 150px; border: 2px solid {cor_ciano_neon}; border-radius: 20px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px {cor_ciano_neon}40; padding: 10px;">
{svg_principal}
</div>
<div>
<h1 style="font-family: 'Rajdhani', sans-serif !important; font-size: 4rem; font-weight: 600; color: #FFFFFF; margin: 0; line-height: 1;">S.A.F.E.R.</h1>
<h2 style="font-family: 'Rajdhani', sans-serif !important; font-size: 1.5rem; font-weight: 400; color: {cor_texto_subtitulo}; margin: 0; line-height: 1.2;">Sistema de Análise Facial para Entidades de Risco</h2>
<p style="font-family: 'Rajdhani', sans-serif !important; font-size: 1rem; color: {cor_texto_subtitulo}; margin: 5px 0 0 0;">Reconhecimento facial para apoio à identificação de criminosos</p>
</div>
</div>
<div style="width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; margin-right: 20px;">
{svg_secundaria}
</div>
</div>
"""
