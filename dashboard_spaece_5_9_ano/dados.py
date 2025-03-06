import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

# Configuração do layout para aumentar a largura do conteúdo
st.set_page_config(layout="wide")

# Função para formatar números sem pontos e vírgulas
def formatar_numero(numero):
    return str(numero).replace('.', '').replace(',', '')

# Verificar se os arquivos existem
if not os.path.exists('dashboard_spaece_5_9_ano/xls/result_spaece.xlsx'):
    st.error("Arquivo 'result_spaece.xlsx' não encontrado.")
    st.stop()

if not os.path.exists('dashboard_spaece_5_9_ano/xls/result_alfa.xlsx'):
    st.error("Arquivo 'result_alfa.xlsx' não encontrado.")
    st.stop()

# Carregar os datasets
try:
    result_spaece = pd.read_excel('dashboard_spaece_5_9_ano/xls/result_spaece.xlsx')
    result_alfa = pd.read_excel('dashboard_spaece_5_9_ano/xls/result_alfa.xlsx')
except Exception as e:
    st.error(f"Erro ao carregar os arquivos: {e}")
    st.stop()

# Eliminar coluna 'Unnamed: 0' se existir
result_spaece = result_spaece.loc[:, ~result_spaece.columns.str.contains('^Unnamed')]
result_alfa = result_alfa.loc[:, ~result_alfa.columns.str.contains('^Unnamed')]

# Converter colunas para texto sem pontos e vírgulas
result_spaece['INEP_MUN'] = result_spaece['INEP_MUN'].apply(formatar_numero)
result_spaece['INEP_ESC'] = result_spaece['INEP_ESC'].apply(formatar_numero)
result_spaece['EDICAO'] = result_spaece['EDICAO'].apply(formatar_numero)
result_alfa['INEP_MUN'] = result_alfa['INEP_MUN'].apply(formatar_numero)
result_alfa['INEP_ESC'] = result_alfa['INEP_ESC'].apply(formatar_numero)
result_alfa['EDICAO'] = result_alfa['EDICAO'].apply(formatar_numero)

# Limitar valores a 2 casas decimais
def limitar_decimais(valor):
    if isinstance(valor, (int, float)):
        return round(valor, 2)
    return valor

result_spaece = result_spaece.applymap(limitar_decimais)
result_alfa = result_alfa.applymap(limitar_decimais)

# Sidebar com logotipo e instruções de uso
st.sidebar.image('dashboard_spaece_5_9_ano/img/logo_2021.png', width=300)
st.sidebar.title("Instruções de Uso")
st.sidebar.write("""
1. Selecione o município, escola e etapa.
2. Visualize a tabela de resultados.
3. Explore os gráficos gerados.
4. Faça o download dos gráficos e tabelas.
""")

# Título principal e subtítulo
st.title("📊 Dashboard de Análise de Desempenho Escolar -SPAECE (2012 - 2023)")
st.subheader("Selecione os filtros abaixo para visualizar os dados")

# Divisão em colunas para os seletores
col1, col2, col3 = st.columns(3)

with col1:
    municipio = st.selectbox('Selecione o Município', result_spaece['MUNICIPIO'].unique())

with col2:
    escola = st.selectbox('Selecione a Escola', result_spaece[result_spaece['MUNICIPIO'] == municipio]['ESCOLA'].unique())

with col3:
    etapa = st.selectbox('Selecione a Etapa', ['2º Ano', '5º Ano', '9º Ano'])

# Filtrar os dados com base nas seleções
if etapa in ['5º Ano', '9º Ano']:
    filtered_data = result_spaece[(result_spaece['MUNICIPIO'] == municipio) & 
                                  (result_spaece['ESCOLA'] == escola) & 
                                  (result_spaece['ETAPA'] == etapa)]
else:
    filtered_data = result_alfa[(result_alfa['MUNICIPIO'] == municipio) & 
                                (result_alfa['ESCOLA'] == escola) & 
                                (result_alfa['ETAPA'] == etapa)]

# Verificar se os dados filtrados estão vazios
if filtered_data.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # Exibir a tabela de resultados
    st.write("### Tabela de Resultados")
    st.dataframe(filtered_data, use_container_width=True)

    # Gráficos de PROFICIENCIA_MEDIA por EDICAO e COMPONENTE_CURRICULAR (MATEMÁTICA e LÍNGUA PORTUGUESA)
    st.write("### Gráficos de Proficiência Média por Edição e Componente Curricular")
    
    # Filtrar dados para Matemática e Língua Portuguesa
    matematica_data = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'MATEMÁTICA']
    portugues_data = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'LÍNGUA PORTUGUESA']

    # Gráfico para Matemática
    if not matematica_data.empty:
        st.write("#### Matemática")
        fig_mat, ax_mat = plt.subplots(figsize=(8, 4))
        sns.barplot(data=matematica_data, x='EDICAO', y='PROFICIENCIA_MEDIA', ax=ax_mat)
        ax_mat.set_ylabel('Proficiência Média')
        ax_mat.set_xlabel('Edição')
        ax_mat.set_title(f'Proficiência Média em Matemática - {escola} ({etapa})')
        
        # Adicionar rótulos acima das barras
        for p in ax_mat.patches:
            ax_mat.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Salvar o gráfico em um buffer de bytes
        buf_mat = io.BytesIO()
        plt.savefig(buf_mat, format='png')
        buf_mat.seek(0)

        # Botão de download do gráfico
        st.download_button(
            label="Download do Gráfico de Matemática",
            data=buf_mat,
            file_name=f"proficiencia_matematica_{escola}_{etapa}.png",
            mime="image/png"
        )
        st.pyplot(fig_mat)

    # Gráfico para Língua Portuguesa
    if not portugues_data.empty:
        st.write("#### Língua Portuguesa")
        fig_port, ax_port = plt.subplots(figsize=(8, 4))
        sns.barplot(data=portugues_data, x='EDICAO', y='PROFICIENCIA_MEDIA', ax=ax_port)
        ax_port.set_ylabel('Proficiência Média')
        ax_port.set_xlabel('Edição')
        ax_port.set_title(f'Proficiência Média em Língua Portuguesa - {escola} ({etapa})')
        
        # Adicionar rótulos acima das barras
        for p in ax_port.patches:
            ax_port.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                             ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                             textcoords='offset points')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Salvar o gráfico em um buffer de bytes
        buf_port = io.BytesIO()
        plt.savefig(buf_port, format='png')
        buf_port.seek(0)

        # Botão de download do gráfico
        st.download_button(
            label="Download do Gráfico de Língua Portuguesa",
            data=buf_port,
            file_name=f"proficiencia_portugues_{escola}_{etapa}.png",
            mime="image/png"
        )
        st.pyplot(fig_port)

    # Função para criar gráficos de barras empilhadas por EDICAO em uma única visualização (barras horizontais)
    def criar_grafico_empilhado_unificado(tabela, etapa, componente_curricular, escola):
        if etapa == '2º Ano':
            categories = ['NAO_ALFABETIZADOS', 'ALFABETIZACAO_INCOMPLETA', 'INTERMEDIARIO', 'SUFICIENTE', 'DESEJAVEL']
            colors = ['red', 'orange', 'yellow', 'lightgreen', 'darkgreen']
        elif etapa in ['5º Ano', '9º Ano']:
            categories = ['MUITO_CRITICO', 'CRITICO', 'INTERMEDIARIO', 'ADEQUADO']
            colors = ['red', 'yellow', 'lightgreen', 'darkgreen']
        else:
            st.warning("Etapa não suportada para gráficos empilhados.")
            return

        # Agrupar dados por EDICAO
        grouped_data = tabela.groupby('EDICAO')[categories].sum()

        # Calcular percentuais para cada EDICAO
        percentuais = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

        # Criar figura e eixo
        fig, ax = plt.subplots(figsize=(10, len(percentuais) * 0.8))
        y_positions = range(len(percentuais))

        # Criar barras empilhadas para cada EDICAO
        for i, (edicao, percentuais_edicao) in enumerate(percentuais.iterrows()):
            left = 0
            for j, (category, color) in enumerate(zip(categories, colors)):
                ax.barh(y_positions[i], percentuais_edicao[category], left=left, color=color, label=category if i == 0 else "")
                left += percentuais_edicao[category]

            # Adicionar rótulos
            left = 0
            for j, (category, color) in enumerate(zip(categories, colors)):
                width = percentuais_edicao[category]
                if width > 0:
                    label_color = 'white' if color in ['darkgreen', 'red'] else 'black'
                    ax.text(left + width / 2, y_positions[i], f'{width:.1f}%', ha='center', va='center', color=label_color, fontsize=8)
                left += width

        # Configurar eixo Y com as edições
        ax.set_yticks(y_positions)
        ax.set_yticklabels(percentuais.index)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentual')
        ax.set_title(f'Distribuição Percentual - {componente_curricular} - {escola} ({etapa})')

        # Remover bordas desnecessárias
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Adicionar legenda
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')

        plt.tight_layout()

        # Salvar o gráfico empilhado em um buffer de bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        # Botão de download do gráfico empilhado
        st.download_button(
            label=f"Download do Gráfico Empilhado - {componente_curricular}",
            data=buf,
            file_name=f"grafico_empilhado_{componente_curricular.lower()}_{escola}_{etapa}.png",
            mime="image/png"
        )
        st.pyplot(fig)

    # Aplicar a função para criar gráficos de barras empilhadas unificados
    if etapa in ['2º Ano', '5º Ano', '9º Ano']:
        st.write("### Gráficos de Barras Empilhadas por Edição")
        
        # Filtrar dados para LÍNGUA PORTUGUESA e MATEMÁTICA
        tabela_portugues = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'LÍNGUA PORTUGUESA'].copy()
        tabela_matematica = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'MATEMÁTICA'].copy()

        # Gráficos para Língua Portuguesa
        if not tabela_portugues.empty:
            criar_grafico_empilhado_unificado(tabela_portugues, etapa, "LÍNGUA PORTUGUESA", escola)
        
        # Gráficos para Matemática
        if not tabela_matematica.empty:
            criar_grafico_empilhado_unificado(tabela_matematica, etapa, "MATEMÁTICA", escola)

    # Tabela de variação por Edição
st.write("### Tabela de Variação por Edição")

# Filtrar dados para LÍNGUA PORTUGUESA e MATEMÁTICA
tabela_portugues = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'LÍNGUA PORTUGUESA'].copy()
tabela_matematica = filtered_data[filtered_data['COMPONENTE_CURRICULAR'] == 'MATEMÁTICA'].copy()

# Função para processar e exibir a tabela
def processar_tabela(tabela, componente):
    if not tabela.empty:
        st.write(f"#### {componente}")
        
        # Converter PROFICIENCIA_MEDIA para números inteiros
        tabela['PROFICIENCIA_MEDIA'] = tabela['PROFICIENCIA_MEDIA'].astype(int)
        
        # Calcular variação percentual e diferença de proficiência
        tabela['Variação Percentual'] = tabela['PROFICIENCIA_MEDIA'].pct_change() * 100
        tabela['Diferença de Proficiência'] = tabela['PROFICIENCIA_MEDIA'].diff()
        
        # Formatar diferença e variação percentual
        def formatar_variacao(valor, coluna):
            if pd.isna(valor):
                return "N/A"
            if coluna == 'Variação Percentual':
                return f"{'+' if valor > 0 else '-'} {abs(valor):.1f}%"
            elif coluna == 'Diferença de Proficiência':
                return f"{'+' if valor > 0 else '-'} {abs(valor):.1f}"
            return f"{'↑' if valor > 0 else '↓'} {abs(valor):.1f}"
        
        # Aplicar formatação específica para cada coluna
        tabela['Diferença de Proficiência'] = tabela['Diferença de Proficiência'].apply(
            lambda x: formatar_variacao(x, 'Diferença de Proficiência')
        )
        tabela['Variação Percentual'] = tabela['Variação Percentual'].apply(
            lambda x: formatar_variacao(x, 'Variação Percentual')
        )
        
        # Adicionar coluna de período
        tabela['PERÍODO'] = tabela['EDICAO'].astype(str) + '-' + tabela['EDICAO'].shift(1).astype(str)
        
        # Aplicar cores apenas nas colunas de Diferença e Variação
        def colorir_variacao(valor):
            if pd.isna(valor):
                return "color: blue;"
            if isinstance(valor, str):  # Verifica se o valor é uma string
                if '+' in valor:
                    return "color: green;"
                elif '-' in valor:
                    return "color: red;"
            return "color: black;"
        
        # Selecionar e estilizar as colunas desejadas
        styled_table = tabela[['EDICAO', 'PERÍODO', 'PROFICIENCIA_MEDIA', 'Diferença de Proficiência', 'Variação Percentual']].style.applymap(
            colorir_variacao, subset=['Diferença de Proficiência', 'Variação Percentual']  # Aplica cores apenas nessas colunas
        )
        
        # Exibir tabela
        st.write(styled_table.to_html(), unsafe_allow_html=True)
    else:
        st.warning(f"Nenhum dado encontrado para {componente}.")

# Exibir tabela para LÍNGUA PORTUGUESA
processar_tabela(tabela_portugues, "LÍNGUA PORTUGUESA")

# Exibir tabela para MATEMÁTICA
processar_tabela(tabela_matematica, "MATEMÁTICA")

# Adicionar nota de rodapé
st.markdown(
    """
    <p style='color: red; font-size: 14px;'>
        * A <b>PROFICIENCIA MEDIA</b> está em valores aproximados.
    </p>
    """,
    unsafe_allow_html=True
)

# Adicionar referência com link clicável
st.markdown(
    f"""
    <p style='font-size: 14px;'>
        <b>Fonte:</b> SEDUC. Resultados SPAECE. Disponível em: 
        <a href="https://www.seduc.ce.gov.br/spaece/" target="_blank">https://www.seduc.ce.gov.br/spaece/</a>. Ano 2023.
    </p>
    """,
    unsafe_allow_html=True
)

# Rodapé com copyright
st.markdown("---")
st.markdown("© 2024 - Todos os direitos reservados. Desenvolvido por Setor de Processamento e Monitoramento de Resultados - SPMR/DAM.")