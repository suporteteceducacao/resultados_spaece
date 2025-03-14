import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
from fpdf import FPDF

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
tab1, tab2, tab3 = st.tabs(["Dashboard", "Classificação por Edição", "Classificação da Escola"])

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
