import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
from fpdf import FPDF
from PIL import Image
import tempfile

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
st.title("📊 Dashboard de Análise de Desempenho por Escola e Municipío / SPAECE (2012 - 2023)")
st.subheader("Selecione os filtros abaixo para visualizar os dados")

# Criar abas
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Classificação por Edição", "Classificação da Escola", "Quartil"])

with tab1:
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

            # Ordenar dados por EDICAO
            matematica_data = matematica_data.sort_values(by='EDICAO')

            fig_mat, ax_mat = plt.subplots(figsize=(8, 4))
            sns.barplot(data=matematica_data, x='EDICAO', y='PROFICIENCIA_MEDIA', ax=ax_mat)
            ax_mat.set_ylabel('Proficiência Média')
            ax_mat.set_xlabel('Edição')
            ax_mat.set_title(f'Proficiência Média em Matemática - {escola} ({etapa})')
            
            # Adicionar rótulos acima das barras
            for p in ax_mat.patches:
                ax_mat.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
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

            # Ordenar dados por EDICAO
            portugues_data = portugues_data.sort_values(by='EDICAO')

            fig_port, ax_port = plt.subplots(figsize=(8, 4))
            sns.barplot(data=portugues_data, x='EDICAO', y='PROFICIENCIA_MEDIA', ax=ax_port)
            ax_port.set_ylabel('Proficiência Média')
            ax_port.set_xlabel('Edição')
            ax_port.set_title(f'Proficiência Média em Língua Portuguesa - {escola} ({etapa})')
            
            # Adicionar rótulos acima das barras
            for p in ax_port.patches:
                ax_port.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
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

                # Ordenar tabela por EDICAO
                tabela = tabela.sort_values(by='EDICAO')  # Adicione essa linha
                
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
                styled_table = tabela[['ESCOLA','EDICAO', 'PERÍODO', 'PROFICIENCIA_MEDIA', 'Diferença de Proficiência', 'Variação Percentual']].style.applymap(
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


# Função para gerar o PDF
def gerar_pdf(df_filtrado, edicao_selecionada):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Adicionar a logo
    logo_path = 'dashboard_spaece_5_9_ano/img/logo_2021.png'
    pdf.image(logo_path, x=60, y=10, w=90)  # Ajuste a posição e o tamanho da logo

    # Adicionar título e subtítulo
    pdf.set_font("Arial", 'B', 16)
    pdf.ln(40)  # Espaço após a logo
    pdf.cell(0, 10, "SETOR DE MONITORAMENTO E PROCESSAMENTO DE RESULTADOS", ln=True, align='C')
    pdf.cell(0, 10, "Ranking SPAECE", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Edição: {edicao_selecionada}", ln=True, align='C')

    # Configurações da tabela
    pdf.set_font("Arial", 'B', 10)  # Fonte menor para o cabeçalho
    pdf.set_fill_color(0, 51, 102)  # Azul escuro para o cabeçalho
    pdf.set_text_color(255, 255, 255)  # Texto branco

    # Definir larguras das colunas
    col_widths = [15, 60, 20, 25, 50, 20]  # Larguras ajustadas para cada coluna

    # Cabeçalho da tabela
    headers = ["ORD", "ESCOLA", "ETAPA", "PROFICIÊNCIA", "COMPONENTE", "EDIÇÃO"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', fill=True)
    pdf.ln()

    # Preencher a tabela com os dados
    pdf.set_font("Arial", '', 8)  # Fonte menor para o conteúdo
    pdf.set_text_color(0, 0, 0)  # Texto preto

    for index, row in df_filtrado.iterrows():
        # ORD
        pdf.cell(col_widths[0], 10, row['ORD'], 1, 0, 'C')
        
        # ESCOLA (com quebra de texto dentro da célula, sem bordas internas)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(col_widths[1], 10, row['ESCOLA'], 0, 'L')  # Sem bordas internas (0 no lugar de 1)
        pdf.set_xy(x + col_widths[1], y)  # Reposiciona o cursor para a próxima coluna
        
        # ETAPA
        pdf.cell(col_widths[2], 10, row['ETAPA'], 1, 0, 'C')
        
        # PROFICIÊNCIA
        pdf.cell(col_widths[3], 10, str(row['PROFICIENCIA_MEDIA']), 1, 0, 'C')
        
        # COMPONENTE
        pdf.cell(col_widths[4], 10, row['COMPONENTE_CURRICULAR'], 1, 0, 'L')
        
        # EDIÇÃO
        pdf.cell(col_widths[5], 10, str(row['EDICAO']), 1, 1, 'C')

    # Salvar o PDF em um buffer de bytes
    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return pdf_output

# ... (código anterior até a aba "Classificação")

with tab2:
    # Nova aba de Classificação por Proficiência Média
    st.header("Classificação por Proficiência Média")
    
    # Seletores para ETAPA, COMPONENTE CURRICULAR e EDIÇÃO
    col1, col2, col3 = st.columns(3)
    with col1:
        etapa_selecionada = st.selectbox("Selecione a ETAPA", ['2º Ano', '5º Ano', '9º Ano'], key="etapa_classificacao")
    with col2:
        componente_selecionado = st.selectbox("Selecione o COMPONENTE CURRICULAR", result_spaece['COMPONENTE_CURRICULAR'].unique(), key="componente_classificacao")
    with col3:
        edicao_selecionada = st.selectbox("Selecione a EDIÇÃO", sorted(result_spaece['EDICAO'].unique()), key="edicao_classificacao")
    
    # Escolher o banco de dados correto com base na etapa selecionada
    if etapa_selecionada == '2º Ano':
        df_filtrado = result_alfa[
            (result_alfa['ETAPA'] == etapa_selecionada) &
            (result_alfa['COMPONENTE_CURRICULAR'] == componente_selecionado) &
            (result_alfa['EDICAO'] == edicao_selecionada)
        ]
    else:
        df_filtrado = result_spaece[
            (result_spaece['ETAPA'] == etapa_selecionada) &
            (result_spaece['COMPONENTE_CURRICULAR'] == componente_selecionado) &
            (result_spaece['EDICAO'] == edicao_selecionada)
        ]

    # Verificar se há dados filtrados
    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Ordenar por PROFICIENCIA_MEDIA do maior para o menor
        df_filtrado = df_filtrado.sort_values(by='PROFICIENCIA_MEDIA', ascending=False)

        # Adicionar coluna ORD com a classificação ordinal (1º, 2º, 3º, etc.)
        df_filtrado['ORD'] = df_filtrado['PROFICIENCIA_MEDIA'].rank(method='min', ascending=False).astype(int)
        df_filtrado['ORD'] = df_filtrado['ORD'].apply(lambda x: f"{int(x)}º")

        # Selecionar as colunas desejadas
        df_filtrado = df_filtrado[['ORD', 'ESCOLA', 'ETAPA', 'PROFICIENCIA_MEDIA', 'COMPONENTE_CURRICULAR', 'EDICAO']]

        # Exibir o DataFrame
        st.write("### Classificação por Proficiência Média")
        st.dataframe(df_filtrado, use_container_width=True)

        # Botão para download do DataFrame em CSV
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download da Classificação (CSV)",
            data=csv,
            file_name=f"classificacao_{etapa_selecionada}_{componente_selecionado}_{edicao_selecionada}.csv",
            mime="text/csv"
        )

        # Botão para gerar e baixar o PDF
        if st.button("Gerar PDF da Classificação"):
            pdf_output = gerar_pdf(df_filtrado, edicao_selecionada)

            # Botão de download do PDF
            st.download_button(
                label="Download da Classificação (PDF)",
                data=pdf_output,
                file_name=f"classificacao_{etapa_selecionada}_{componente_selecionado}_{edicao_selecionada}.pdf",
                mime="application/pdf"
            )
with tab3:
    # Nova aba de Classificação da Escola em Todas as Edições
    st.header("Classificação da Escola em Todas as Edições")

    # Seletores para ESCOLA, ETAPA e COMPONENTE CURRICULAR
    col1, col2, col3 = st.columns(3)
    with col1:
        escola_selecionada = st.selectbox("Selecione a ESCOLA", result_spaece['ESCOLA'].unique(), key="escola_classificacao_tab3")
    with col2:
        etapa_escola = st.selectbox("Selecione a ETAPA", ['2º Ano', '5º Ano', '9º Ano'], key="etapa_escola_tab3")
    with col3:
        componente_escola = st.selectbox("Selecione o COMPONENTE CURRICULAR", result_spaece['COMPONENTE_CURRICULAR'].unique(), key="componente_escola_tab3")

    # Escolher o banco de dados correto com base na etapa selecionada
    if etapa_escola == '2º Ano':
        df_escola_filtrado = result_alfa[
            (result_alfa['ESCOLA'] == escola_selecionada) &
            (result_alfa['ETAPA'] == etapa_escola) &
            (result_alfa['COMPONENTE_CURRICULAR'] == componente_escola)
        ]
    else:
        df_escola_filtrado = result_spaece[
            (result_spaece['ESCOLA'] == escola_selecionada) &
            (result_spaece['ETAPA'] == etapa_escola) &
            (result_spaece['COMPONENTE_CURRICULAR'] == componente_escola)
        ]

    # Verificar se há dados filtrados
    if df_escola_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Calcular a posição da escola em cada edição
        if etapa_escola == '2º Ano':
            df_posicao_escola = result_alfa[
                (result_alfa['ETAPA'] == etapa_escola) &
                (result_alfa['COMPONENTE_CURRICULAR'] == componente_escola)
            ]
        else:
            df_posicao_escola = result_spaece[
                (result_spaece['ETAPA'] == etapa_escola) &
                (result_spaece['COMPONENTE_CURRICULAR'] == componente_escola)
            ]

        # Ordenar por EDICAO e PROFICIENCIA_MEDIA (decrescente)
        df_posicao_escola = df_posicao_escola.sort_values(by=['EDICAO', 'PROFICIENCIA_MEDIA'], ascending=[True, False])

        # Calcular a posição de cada escola em cada edição
        df_posicao_escola['POSICAO'] = df_posicao_escola.groupby('EDICAO')['PROFICIENCIA_MEDIA'].rank(method='min', ascending=False).astype(int)

        # Filtrar apenas os dados da escola selecionada
        df_posicao_escola = df_posicao_escola[df_posicao_escola['ESCOLA'] == escola_selecionada]

        # Formatar a posição como ordinal (1º, 2º, 3º, etc.)
        df_posicao_escola['POSICAO'] = df_posicao_escola['POSICAO'].apply(lambda x: f"{int(x)}º")

        # Selecionar as colunas desejadas
        df_posicao_escola = df_posicao_escola[['EDICAO', 'ESCOLA', 'ETAPA', 'COMPONENTE_CURRICULAR', 'PROFICIENCIA_MEDIA', 'POSICAO']]

        # Ordenar por EDICAO
        df_posicao_escola = df_posicao_escola.sort_values(by='EDICAO')

        # Exibir o DataFrame
        st.write(f"### Classificação da Escola {escola_selecionada} em Todas as Edições")
        st.dataframe(df_posicao_escola, use_container_width=True)

        # Botão para download do DataFrame em CSV
        csv_escola = df_posicao_escola.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download da Classificação da Escola (CSV)",
            data=csv_escola,
            file_name=f"classificacao_escola_{escola_selecionada}_{etapa_escola}_{componente_escola}.csv",
            mime="text/csv"
        )


with tab4:
    st.header("📊 Análise por Quartis de Proficiência")
    
    # Contêiner para os seletores
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            filtro_escola = st.selectbox("Filtrar por:", ['Todas as Escolas', 'Escola Específica'], key="filtro_escola")
            etapa_quartil = st.selectbox("Selecione a ETAPA", ['2º Ano', '5º Ano', '9º Ano'], key="etapa_quartil")
        
        with col2:
            if filtro_escola == 'Escola Específica':
                # Carrega escolas conforme etapa selecionada
                if etapa_quartil == '2º Ano':
                    escolas_options = result_alfa[result_alfa['ETAPA'] == '2º Ano']['ESCOLA'].unique()
                else:
                    escolas_options = result_spaece[result_spaece['ETAPA'] == etapa_quartil]['ESCOLA'].unique()
                
                escola_selecionada = st.selectbox("Selecione a ESCOLA", sorted(escolas_options), key="escola_quartil")
            else:
                # Filtra edições disponíveis conforme a etapa
                if etapa_quartil == '2º Ano':
                    edicoes_disponiveis = sorted(result_alfa['EDICAO'].unique())
                else:
                    edicoes_disponiveis = sorted(result_spaece[result_spaece['ETAPA'] == etapa_quartil]['EDICAO'].unique())
                
                edicao_quartil = st.selectbox("Selecione a EDIÇÃO", edicoes_disponiveis, key="edicao_quartil")
            
            componente_quartil = st.selectbox("Selecione o COMPONENTE", 
                                            ['MATEMÁTICA', 'LÍNGUA PORTUGUESA'], 
                                            key="componente_quartil")

    # Processamento dos dados
    if filtro_escola == 'Escola Específica':
        try:
            if etapa_quartil == '2º Ano':
                df_escola = result_alfa[
                    (result_alfa['ESCOLA'] == escola_selecionada) & 
                    (result_alfa['ETAPA'] == '2º Ano') &
                    (result_alfa['COMPONENTE_CURRICULAR'] == componente_quartil)
                ].copy()
            else:
                df_escola = result_spaece[
                    (result_spaece['ESCOLA'] == escola_selecionada) & 
                    (result_spaece['ETAPA'] == etapa_quartil) &
                    (result_spaece['COMPONENTE_CURRICULAR'] == componente_quartil)
                ].copy()
            
            if df_escola.empty:
                st.warning(f"Nenhum dado encontrado para a escola {escola_selecionada} na etapa {etapa_quartil}")
            else:
                # Processa cada edição para classificar nos quartis
                resultados = []
                for edicao in df_escola['EDICAO'].unique():
                    # Filtra dados da edição específica
                    if etapa_quartil == '2º Ano':
                        df_edicao = result_alfa[
                            (result_alfa['EDICAO'] == edicao) &
                            (result_alfa['ETAPA'] == '2º Ano') &
                            (result_alfa['COMPONENTE_CURRICULAR'] == componente_quartil)
                        ].copy()
                    else:
                        df_edicao = result_spaece[
                            (result_spaece['EDICAO'] == edicao) &
                            (result_spaece['ETAPA'] == etapa_quartil) &
                            (result_spaece['COMPONENTE_CURRICULAR'] == componente_quartil)
                        ].copy()
                    
                    if not df_edicao.empty:
                        # Garante que a proficiência é numérica
                        df_edicao['PROFICIENCIA_MEDIA'] = pd.to_numeric(df_edicao['PROFICIENCIA_MEDIA'], errors='coerce')
                        df_edicao = df_edicao.dropna(subset=['PROFICIENCIA_MEDIA'])
                        
                        if not df_edicao.empty:
                            q1, q2, q3 = df_edicao['PROFICIENCIA_MEDIA'].quantile([0.25, 0.5, 0.75])
                            prof_escola = float(df_escola[df_escola['EDICAO'] == edicao]['PROFICIENCIA_MEDIA'].values[0])
                            
                            # Classifica o quartil
                            if prof_escola <= q1:
                                quartil = "Q1 (25% piores)"
                            elif prof_escola <= q2:
                                quartil = "Q2 (25% básicas)"
                            elif prof_escola <= q3:
                                quartil = "Q3 (25% intermediárias)"
                            else:
                                quartil = "Q4 (25% melhores)"
                            
                            resultados.append({
                                'ESCOLA': escola_selecionada,
                                'EDIÇÃO': edicao,
                                'PROFICIÊNCIA': prof_escola,
                                'QUARTIL': quartil,
                                'Q1': q1,
                                'MEDIANA (Q2)': q2,
                                'Q3': q3
                            })
                
                if resultados:
                    df_resultado = pd.DataFrame(resultados).sort_values('EDIÇÃO')
                    
                    # Exibe tabela com estilo
                    def color_quartil(val):
                        color = 'red' if 'Q1' in val else 'orange' if 'Q2' in val else 'lightgreen' if 'Q3' in val else 'darkgreen'
                        return f'color: {color}; font-weight: bold'
                    
                    st.dataframe(
                        df_resultado.style.format({
                            'PROFICIÊNCIA': '{:.1f}',
                            'Q1': '{:.1f}',
                            'MEDIANA (Q2)': '{:.1f}',
                            'Q3': '{:.1f}'
                        }).applymap(color_quartil, subset=['QUARTIL']),
                        use_container_width=True
                    )
                    
                    # Gera gráfico de evolução
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    # Plot principal com rótulos
                    line = ax.plot(df_resultado['EDIÇÃO'], df_resultado['PROFICIÊNCIA'], 
                                 'b-o', linewidth=2, markersize=8, label=f'Escola: {escola_selecionada}')
                    
                    # Adiciona rótulos de proficiência
                    for idx, row in df_resultado.iterrows():
                        ax.annotate(f"{row['PROFICIÊNCIA']:.1f}", 
                                   (row['EDIÇÃO'], row['PROFICIÊNCIA']),
                                   textcoords="offset points", xytext=(0,10), 
                                   ha='center', fontsize=9, color='blue')
                    
                    # Áreas dos quartis
                    ax.fill_between(df_resultado['EDIÇÃO'], df_resultado['Q1'], df_resultado['MEDIANA (Q2)'], 
                                   color='red', alpha=0.1, label='Q1 (25% piores)')
                    ax.fill_between(df_resultado['EDIÇÃO'], df_resultado['MEDIANA (Q2)'], df_resultado['Q3'], 
                                   color='orange', alpha=0.1, label='Q2 (25% básicas)')
                    ax.fill_between(df_resultado['EDIÇÃO'], df_resultado['Q3'], df_resultado['PROFICIÊNCIA'].max()*1.05, 
                                   color='green', alpha=0.1, label='Q3/Q4 (25% intermediárias/melhores)')
                    
                    # Configurações do gráfico
                    ax.set_title(f"Evolução da Proficiência\n{escola_selecionada} - {componente_quartil} - {etapa_quartil}", pad=20)
                    ax.set_xlabel("Edição")
                    ax.set_ylabel("Proficiência Média")
                    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
                    ax.grid(True, linestyle='--', alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    
                    # Botões de download
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "Download CSV",
                            df_resultado.to_csv(index=False),
                            f"quartis_escola_{escola_selecionada}.csv"
                        )
                    with col2:
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=300)
                        st.download_button(
                            "Download Gráfico",
                            buf.getvalue(),
                            f"evolucao_{escola_selecionada}.png"
                        )
                else:
                    st.warning("Nenhum dado disponível para análise")
        
        except Exception as e:
            st.error(f"Erro ao processar dados: {str(e)}")

    else:
        # Modo Todas as Escolas
        try:
            # Seleciona a base correta com filtro rigoroso por etapa
            if etapa_quartil == '2º Ano':
                df_quartil = result_alfa[
                    (result_alfa['EDICAO'] == edicao_quartil) &
                    (result_alfa['ETAPA'] == '2º Ano') &
                    (result_alfa['COMPONENTE_CURRICULAR'] == componente_quartil)
                ].copy()
            else:
                df_quartil = result_spaece[
                    (result_spaece['EDICAO'] == edicao_quartil) &
                    (result_spaece['ETAPA'] == etapa_quartil) &
                    (result_spaece['COMPONENTE_CURRICULAR'] == componente_quartil)
                ].copy()
            
            # Garante que a proficiência é numérica
            df_quartil['PROFICIENCIA_MEDIA'] = pd.to_numeric(df_quartil['PROFICIENCIA_MEDIA'], errors='coerce')
            df_quartil = df_quartil.dropna(subset=['PROFICIENCIA_MEDIA'])
            
            if df_quartil.empty:
                st.warning(f"Nenhum dado encontrado para {etapa_quartil} na edição {edicao_quartil}")
            else:
                # Calcula quartis
                q1, q2, q3 = df_quartil['PROFICIENCIA_MEDIA'].quantile([0.25, 0.5, 0.75])
                
                # Classifica as escolas
                def classificar_quartil(proficiencia):
                    if proficiencia <= q1:
                        return "Q1 (25% piores)"
                    elif proficiencia <= q2:
                        return "Q2 (25% básicas)"
                    elif proficiencia <= q3:
                        return "Q3 (25% intermediárias)"
                    else:
                        return "Q4 (25% melhores)"
                
                df_quartil['QUARTIL'] = df_quartil['PROFICIENCIA_MEDIA'].apply(classificar_quartil)
                
                # Função para colorir as células da tabela
                def colorir_quartil(val):
                    if 'Q1' in val: color = '#ffcccc'
                    elif 'Q2' in val: color = '#ffe6cc'
                    elif 'Q3' in val: color = '#e6f7e6'
                    else: color = '#ccf2ff'
                    return f'background-color: {color}; font-weight: bold'
                
                # Exibe tabela com escolas
                st.write("### Classificação por Quartis")
                st.dataframe(
                    df_quartil[['ESCOLA', 'ETAPA', 'COMPONENTE_CURRICULAR', 'EDICAO', 'PROFICIENCIA_MEDIA', 'QUARTIL']]
                    .sort_values('PROFICIENCIA_MEDIA', ascending=False)
                    .style.applymap(colorir_quartil, subset=['QUARTIL'])
                    .format({'PROFICIENCIA_MEDIA': '{:.1f}'}),
                    use_container_width=True,
                    height=400
                )
                
                # Botão para gerar PDF
                if st.button("📄 Gerar PDF da Classificação"):
                    def gerar_pdf_classificacao(df, componente, etapa, edicao):
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.add_page()
                        
                        # Logo (ajuste o caminho conforme necessário)
                        logo_path = 'dashboard_spaece_5_9_ano/img/logo_2021.png'
                        if os.path.exists(logo_path):
                            pdf.image(logo_path, x=10, y=8, w=30)
                        
                        # Título e subtítulo
                        pdf.set_font('Arial', 'B', 16)
                        pdf.cell(0, 20, "Classificação por Quartis de Proficiência", ln=True, align='C')
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, f"Componente: {componente} | Etapa: {etapa} | Edição: {edicao}", ln=True, align='C')
                        pdf.ln(10)
                        
                        # Configuração da tabela
                        pdf.set_font('Arial', 'B', 10)
                        
                        # Cabeçalho da tabela (fundo azul e texto branco)
                        pdf.set_fill_color(0, 51, 102)
                        pdf.set_text_color(255, 255, 255)
                        
                        # Larguras das colunas
                        col_widths = [15, 60, 20, 25, 30]
                        
                        # Cabeçalhos
                        headers = ["Pos.", "Escola", "Etapa", "Proficiência", "Quartil"]
                        for i, header in enumerate(headers):
                            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', fill=True)
                        pdf.ln()
                        
                        # Conteúdo da tabela
                        pdf.set_font('Arial', '', 8)
                        pdf.set_text_color(0, 0, 0)
                        
                        # Ordena o DataFrame
                        df_sorted = df.sort_values('PROFICIENCIA_MEDIA', ascending=False)
                        df_sorted['POSICAO'] = range(1, len(df_sorted) + 1)
                        
                        # Cores para os quartis
                        quartil_colors = {
                            "Q1 (25% piores)": (255, 204, 204),
                            "Q2 (25% básicas)": (255, 229, 204),
                            "Q3 (25% intermediárias)": (204, 255, 204),
                            "Q4 (25% melhores)": (204, 255, 255)
                        }
                        
                        for _, row in df_sorted.iterrows():
                            # Posição
                            pdf.cell(col_widths[0], 10, str(row['POSICAO']), 1, 0, 'C')
                            
                            # Escola (com quebra de linha)
                            pdf.multi_cell(col_widths[1], 10, row['ESCOLA'], 1, 'L')
                            pdf.set_xy(pdf.get_x() + col_widths[0] + col_widths[1], pdf.get_y() - 10)
                            
                            # Etapa
                            pdf.cell(col_widths[2], 10, row['ETAPA'], 1, 0, 'C')
                            
                            # Proficiência
                            pdf.cell(col_widths[3], 10, f"{row['PROFICIENCIA_MEDIA']:.1f}", 1, 0, 'C')
                            
                            # Quartil (com cor de fundo)
                            quartil = row['QUARTIL']
                            color = quartil_colors.get(quartil, (255, 255, 255))
                            pdf.set_fill_color(*color)
                            pdf.cell(col_widths[4], 10, quartil.split(' ')[0], 1, 1, 'C', fill=True)
                            pdf.set_fill_color(255, 255, 255)
                        
                        # Salva em arquivo temporário
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                        pdf_path = temp_file.name
                        pdf.output(pdf_path)
                        temp_file.close()
                        return pdf_path
                    
                    with st.spinner("Gerando PDF..."):
                        try:
                            pdf_path = gerar_pdf_classificacao(
                                df_quartil,
                                componente_quartil,
                                etapa_quartil,
                                edicao_quartil
                            )
                            
                            with open(pdf_path, "rb") as f:
                                pdf_bytes = f.read()
                            
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_bytes,
                                file_name=f"classificacao_quartis_{componente_quartil}_{etapa_quartil}_{edicao_quartil}.pdf",
                                mime="application/pdf"
                            )
                            
                            os.unlink(pdf_path)
                            
                        except Exception as e:
                            st.error(f"Erro ao gerar PDF: {str(e)}")
                
                # Tabela de referência
                st.write("### Valores de Referência dos Quartis")
                df_ref = pd.DataFrame({
                    'Quartil': ['Q1 (25% piores)', 'Q2 (25% básicas)', 'Q3 (25% intermediárias)', 'Q4 (25% melhores)'],
                    'Intervalo': [f"≤ {q1:.1f}", f"{q1:.1f} - {q2:.1f}", f"{q2:.1f} - {q3:.1f}", f"> {q3:.1f}"],
                    'Nº de Escolas': [
                        (df_quartil['QUARTIL'] == "Q1 (25% piores)").sum(),
                        (df_quartil['QUARTIL'] == "Q2 (25% básicas)").sum(),
                        (df_quartil['QUARTIL'] == "Q3 (25% intermediárias)").sum(),
                        (df_quartil['QUARTIL'] == "Q4 (25% melhores)").sum()
                    ]
                })
                st.dataframe(df_ref, use_container_width=True)
                
                # Boxplot com melhorias
                st.write("### Distribuição por Quartis")
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Estilo do boxplot
                boxprops = dict(linestyle='-', linewidth=1.5)
                whiskerprops = dict(linestyle='--')
                medianprops = dict(linestyle='-', linewidth=2.5, color='yellow')
                
                # Cria o boxplot
                sns.boxplot(data=df_quartil, x='QUARTIL', y='PROFICIENCIA_MEDIA', 
                           order=["Q1 (25% piores)", "Q2 (25% básicas)", "Q3 (25% intermediárias)", "Q4 (25% melhores)"], 
                           palette=['#ff9999', '#ffcc99', '#99cc99', '#99ccff'],
                           boxprops=boxprops, whiskerprops=whiskerprops, medianprops=medianprops)
                
                # Linhas de referência
                ax.axhline(y=q1, color='red', linestyle=':', alpha=0.7, label=f'Q1: {q1:.1f}')
                ax.axhline(y=q2, color='orange', linestyle=':', alpha=0.7, label=f'Mediana (Q2): {q2:.1f}')
                ax.axhline(y=q3, color='green', linestyle=':', alpha=0.7, label=f'Q3: {q3:.1f}')
                
                # Rótulos das medianas
                for i, quartil in enumerate(["Q1 (25% piores)", "Q2 (25% básicas)", "Q3 (25% intermediárias)", "Q4 (25% melhores)"]):
                    q_data = df_quartil[df_quartil['QUARTIL'] == quartil]['PROFICIENCIA_MEDIA']
                    median = q_data.median()
                    ax.text(i, median, f'{median:.1f}', ha='center', va='center', 
                           fontweight='bold', color='black', bbox=dict(facecolor='white', alpha=0.8))
                
                # Configurações do gráfico
                ax.set_title(f"Distribuição por Quartis\n{componente_quartil} - {etapa_quartil} (Edição {edicao_quartil})", pad=20)
                ax.set_xlabel("Quartil")
                ax.set_ylabel("Proficiência Média")
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
                ax.grid(True, linestyle='--', alpha=0.3)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # Botões de download
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download CSV",
                        df_quartil[['ESCOLA', 'ETAPA', 'COMPONENTE_CURRICULAR', 'PROFICIENCIA_MEDIA', 'QUARTIL']].to_csv(index=False),
                        f"quartis_{componente_quartil}_{etapa_quartil}_{edicao_quartil}.csv"
                    )
                with col2:
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=300)
                    st.download_button(
                        "Download Gráfico",
                        buf.getvalue(),
                        f"boxplot_quartis_{componente_quartil}_{etapa_quartil}_{edicao_quartil}.png"
                    )
        
        except Exception as e:
            st.error(f"Erro ao processar dados: {str(e)}")
            
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
        st.markdown(f""" <p style='font-size: 14px; text-align: center'> © 2024 - Todos os direitos reservados. <b>Desenvolvido por Setor de Processamento e Monitoramento de Resultados - SPMR/DAM.</b> </p> """, unsafe_allow_html=True
        )
