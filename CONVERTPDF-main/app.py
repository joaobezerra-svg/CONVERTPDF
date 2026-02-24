import streamlit as st
import pandas as pd
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tabula
from fpdf import FPDF
import base64
import io
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CONVERTPDF", page_icon="📄", layout="wide")

# --- BACKGROUND IMAGE CSS ---
def set_background(image_path="background.jpg", base64_string=None):
    if base64_string:
        b64_str = base64_string
    elif os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            b64_str = base64.b64encode(image_file.read()).decode()
    else:
        return

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{b64_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp > header {{
        background-color: transparent;
    }}
    .main .block-container {{
        background-color: rgba(15, 23, 42, 0.85);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply background if image exists
set_background("background.jpg")

st.title("📄 CONVERTPDF")
st.markdown("Bem-vindo ao **CONVERTPDF**! Sua suíte local para gerenciamento e conversão de documentos.")

menu_options = [
    "Juntar PDF", 
    "Dividir PDF", 
    "Comprimir PDF", 
    "PDF para Excel", 
    "Excel para PDF"
]
choice = st.sidebar.selectbox("Escolha uma ferramenta", menu_options)

if choice == "Juntar PDF":
    st.subheader("🔗 Juntar múltiplos arquivos PDF")
    uploaded_files = st.file_uploader("Selecione os arquivos PDF (a ordem de seleção importa)", type="pdf", accept_multiple_files=True)
    
    if st.button("Juntar PDFs") and uploaded_files:
        merger = PdfMerger()
        for pdf in uploaded_files:
            merger.append(pdf)
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        st.success("PDFs juntados com sucesso!")
        st.download_button("Baixar PDF Juntado", data=output.getvalue(), file_name="juntado.pdf", mime="application/pdf")

elif choice == "Dividir PDF":
    st.subheader("✂️ Extrair páginas específicas de um PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF", type="pdf")
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        st.write(f"O PDF possui **{total_pages}** páginas.")
        col1, col2 = st.columns(2)
        start_page = col1.number_input("Página Inicial", min_value=1, max_value=total_pages, value=1)
        end_page = col2.number_input("Página Final", min_value=1, max_value=total_pages, value=total_pages)
        
        if st.button("Dividir PDF"):
            if start_page > end_page:
                st.error("A página inicial deve ser menor ou igual à página final.")
            else:
                writer = PdfWriter()
                for i in range(start_page - 1, end_page):
                    writer.add_page(reader.pages[i])
                output = io.BytesIO()
                writer.write(output)
                st.success("PDF dividido com sucesso!")
                st.download_button("Baixar PDF Dividido", data=output.getvalue(), file_name="dividido.pdf", mime="application/pdf")

elif choice == "Comprimir PDF":
    st.subheader("🗜️ Comprimir um arquivo PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF para compressão", type="pdf")
    if st.button("Comprimir PDF") and uploaded_file:
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams() 
            writer.add_page(page)
        output = io.BytesIO()
        writer.write(output)
        st.success("Compressão executada!")
        st.download_button("Baixar PDF Comprimido", data=output.getvalue(), file_name="comprimido.pdf", mime="application/pdf")

elif choice == "PDF para Excel":
    st.subheader("📊 Converter Tabelas do PDF para Excel (.xlsx)")
    st.info("Requer o Java (JDK) instalado no sistema para a extração do texto.")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF", type="pdf")
    if st.button("Extrair para Excel") and uploaded_file:
        try:
            with st.spinner('Analisando tabelas com o Tabula...'):
                temp_pdf = "temp_uploaded.pdf"
                with open(temp_pdf, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                tabelas = tabula.read_pdf(temp_pdf, pages='all', multiple_tables=True)
                if tabelas:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for i, tab in enumerate(tabelas):
                            tab.to_excel(writer, sheet_name=f'Tabela_{i+1}', index=False)
                    st.success(f"Sucesso! {len(tabelas)} tabela(s) encontrada(s).")
                    st.download_button("Baixar Arquivo Excel", data=output.getvalue(), file_name="tabelas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("Nenhuma tabela encontrada.")
                os.remove(temp_pdf)
        except Exception as e:
            st.error(f"Erro: {e}")

elif choice == "Excel para PDF":
    st.subheader("📑 Converter Tabelas do Excel para PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx", "xls"])
    if st.button("Gerar PDF") and uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df = df.astype(str) # Convert everything to string
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", size=9)
            page_width = pdf.w - 2 * pdf.l_margin
            col_width = page_width / float(len(df.columns))
            row_height = pdf.font_size * 1.5
            
            # Draw header
            pdf.set_font("Arial", 'B', size=9)
            for col in df.columns:
                pdf.cell(col_width, row_height, txt=str(col)[:30], border=1)
            pdf.ln(row_height)
            
            # Draw rows
            pdf.set_font("Arial", size=8)
            for row in df.itertuples(index=False):
                for item in row:
                    pdf.cell(col_width, row_height, txt=str(item)[:40], border=1)
                pdf.ln(row_height)
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.success("Planilha convertida!")
            st.download_button("Baixar PDF", data=pdf_bytes, file_name="planilha.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao processar o Excel: {e}")
