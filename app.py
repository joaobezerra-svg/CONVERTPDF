import streamlit as st
import PyPDF2
import pandas as pd
import tabula
from fpdf import FPDF
import io
import os
import base64
import tempfile
import zipfile

# Dependências extras requeridas
try:
    import pikepdf
except ImportError:
    pikepdf = None

try:
    from pdf2docx import Converter
except ImportError:
    Converter = None

try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfkit
except ImportError:
    pdfkit = None

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import Color
except ImportError:
    canvas = None

def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        bg_css = f'''
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        '''
    else:
        bg_css = '''
        .stApp {
             background: radial-gradient(circle at center, #0B192C 0%, #000000 100%);
        }
        .stApp::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(circle at 10% 50%, rgba(0, 180, 255, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 30%, rgba(0, 255, 255, 0.15) 0%, transparent 40%),
                linear-gradient(45deg, rgba(0, 50, 100, 0.1) 25%, transparent 25%),
                linear-gradient(-45deg, rgba(0, 50, 100, 0.1) 25%, transparent 25%);
            pointer-events: none;
            z-index: -1;
        }
        '''
        
    common_css = f'''
    <style>
    {bg_css}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    [data-testid="stSidebar"] {{
        background-color: #1A1A24 !important;
        border-right: 1px solid #332145 !important;
    }}
    
    .stButton > button {{
        background-color: #B43BE8 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease-in-out !important;
    }}
    
    .stButton > button:hover {{
        background-color: #9226C2 !important;
        box-shadow: 0 0 15px #B43BE8 !important;
        transform: scale(1.05) !important;
    }}
    
    [data-testid="stFileUploadDropzone"] {{
        background-color: #1F1F2E;
        border: 2px dashed #B43BE8 !important;
        border-radius: 12px;
        padding: 30px;
    }}
    
    [data-testid="stFileUploadDropzone"] button {{
        background-color: #333345 !important;
        border: 1px solid #555 !important;
        color: white !important;
        border-radius: 6px !important;
        transition: all 0.3s ease-in-out !important;
    }}
    
    [data-testid="stFileUploadDropzone"] button:hover {{
        background-color: #B43BE8 !important;
        border-color: #B43BE8 !important;
        box-shadow: 0 0 15px #B43BE8 !important;
        transform: scale(1.05) !important;
    }}
    
    .block-container {{
        background-color: rgba(20, 15, 30, 0.75);
        padding: 2rem !important;
        border-radius: 15px;
        box-shadow: 0 0 40px rgba(180, 59, 232, 0.2);
        margin-top: 3rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(180, 59, 232, 0.3);
        animation: fadeIn 0.5s ease-in-out;
    }}

    h1, h2, h3, div[data-testid="stMarkdownContainer"] > p {{
        color: #E2E8F0 !important;
    }}
    h1 {{
        text-shadow: 0 0 20px rgba(180,59,232,0.8);
    }}
    </style>
    '''
    st.markdown(common_css, unsafe_allow_html=True)

def display_pdf(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf" style="border-radius:10px; border:2px solid #B43BE8;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.set_page_config(page_title="CONVERTPDF", page_icon="📄", layout="centered")

if os.path.exists("background.jpg"):
    set_background("background.jpg")
elif os.path.exists("background.png"):
    set_background("background.png")
else:
    set_background("none.jpg")

st.sidebar.title("CONVERTPDF 📄")
st.sidebar.markdown("Escolha uma categoria:")

# Cursos do Menu
categorias = [
    "1. ORGANIZAR", 
    "2. OTIMIZAR", 
    "3. CONVERTER PARA PDF", 
    "4. CONVERTER DE PDF", 
    "5. EDITAR", 
    "6. SEGURANÇA"
]
categoria = st.sidebar.radio("Categorias", categorias)

choice = None

if "1. ORGANIZAR" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["Juntar PDF", "Dividir PDF", "Remover Páginas", "Organizar PDF"])
elif "2. OTIMIZAR" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["Comprimir PDF", "Reparar PDF"])
elif "3. CONVERTER PARA" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["Excel para PDF", "Word para PDF", "JPG para PDF"])
elif "4. CONVERTER DE" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["PDF para Excel", "PDF para Word", "PDF para JPG"])
elif "5. EDITAR" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["Rodar PDF", "Numerar Páginas", "Marca d'água", "Editar Texto"])
elif "6. SEGURANÇA" in categoria:
    choice = st.sidebar.radio("Ferramentas", ["Proteger PDF", "Desbloquear PDF"])

# ----------------- 1. ORGANIZAR -----------------
if choice == "Juntar PDF":
    st.header("Juntar NFTs") # wait, Juntar PDFs
    st.header("Juntar PDF")
    uploaded_files = st.file_uploader("Envie os PDFs que deseja juntar", type='pdf', accept_multiple_files=True)
    if uploaded_files and len(uploaded_files) > 1:
        if st.button("Juntar"):
            merger = PyPDF2.PdfMerger()
            for pdf in uploaded_files:
                merger.append(pdf)
            output = io.BytesIO()
            merger.write(output)
            st.success("PDFs juntados com sucesso!")
            st.download_button("Baixar PDF Juntado", data=output.getvalue(), file_name="juntado.pdf", mime="application/pdf")

elif choice == "Dividir PDF":
    st.header("Dividir PDF")
    uploaded_file = st.file_uploader("Envie o PDF para dividir", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        reader = PyPDF2.PdfReader(uploaded_file)
        num_pages = len(reader.pages)
        st.write(f"O documento contém **{num_pages}** páginas.")
        start_page = int(st.number_input("Da página", min_value=1, max_value=num_pages, value=1))
        end_page = int(st.number_input("Até a página", min_value=start_page, max_value=num_pages, value=num_pages))
        
        if st.button("Dividir"):
            writer = PyPDF2.PdfWriter()
            for i in range(start_page - 1, end_page):
                writer.add_page(reader.pages[i])
            output = io.BytesIO()
            writer.write(output)
            st.success("PDF dividido com sucesso!")
            st.download_button("Baixar Páginas", data=output.getvalue(), file_name="dividido.pdf", mime="application/pdf")

elif choice == "Remover Páginas":
    st.header("Remover Páginas")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        pages_to_remove = st.text_input("Páginas a remover (separadas por vírgula. Ex: 1, 3, 5)")
        if st.button("Remover"):
            reader = PyPDF2.PdfReader(uploaded_file)
            writer = PyPDF2.PdfWriter()
            to_remove = []
            if pages_to_remove:
                to_remove = [int(p.strip()) - 1 for p in pages_to_remove.split(",") if p.strip().isdigit()]
            
            for i in range(len(reader.pages)):
                if i not in to_remove:
                    writer.add_page(reader.pages[i])
            output = io.BytesIO()
            writer.write(output)
            st.success("Páginas removidas com sucesso!")
            st.download_button("Baixar PDF", data=output.getvalue(), file_name="removido.pdf", mime="application/pdf")

elif choice == "Organizar PDF":
    st.header("Organizar PDF (Reordenar)")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        reader = PyPDF2.PdfReader(uploaded_file)
        st.write(f"Documento com **{len(reader.pages)}** páginas.")
        new_order = st.text_input("Nova ordem das páginas (Ex: 3, 1, 2)")
        if st.button("Organizar"):
            writer = PyPDF2.PdfWriter()
            order = [int(p.strip()) - 1 for p in new_order.split(",") if p.strip().isdigit()]
            try:
                for i in order:
                    writer.add_page(reader.pages[i])
                output = io.BytesIO()
                writer.write(output)
                st.success("PDF reorganizado com sucesso!")
                st.download_button("Baixar PDF", data=output.getvalue(), file_name="organizado.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro na numeração: {e}")

# ----------------- 2. OTIMIZAR -----------------
elif choice == "Comprimir PDF":
    st.header("Comprimir PDF")
    uploaded_file = st.file_uploader("Envie o PDF para comprimir", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Comprimir"):
            reader = PyPDF2.PdfReader(uploaded_file)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                if hasattr(page, 'compress_content_streams'):
                    page.compress_content_streams()
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            st.success("Compressão executada!")
            st.download_button("Baixar Comprimido", data=output.getvalue(), file_name="comprimido.pdf", mime="application/pdf")

elif choice == "Reparar PDF":
    st.header("Reparar PDF")
    st.info("Utiliza a biblioteca pikepdf para reparar estruturas de PDFs corrompidas.")
    uploaded_file = st.file_uploader("Envie o PDF corrompido", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Reparar"):
            if not pikepdf:
                st.error("A biblioteca 'pikepdf' não está instalada. Instale via requirements.txt.")
            else:
                try:
                    pdf = pikepdf.open(uploaded_file)
                    output = io.BytesIO()
                    pdf.save(output)
                    st.success("PDF reparado com sucesso!")
                    st.download_button("Baixar PDF Reparado", data=output.getvalue(), file_name="reparado.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Não foi possível reparar: {e}")

# ----------------- 3. CONVERTER PARA PDF -----------------
elif choice == "Excel para PDF":
    st.header("Excel para PDF")
    uploaded_file = st.file_uploader("Envie sua Planilha", type=['xlsx', 'xls'])
    if uploaded_file:
        if st.button("Converter para PDF"):
            try:
                df = pd.read_excel(uploaded_file)
                df = df.astype(str)
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                pdf.set_font("Arial", size=8)
                
                col_width = max(10, 190 / max(1, len(df.columns)))
                row_height = pdf.font_size * 2
                
                # Cabeçalhos com fonte negrito
                pdf.set_font("Arial", 'B', 8)
                for col in df.columns:
                    pdf.cell(col_width, row_height, str(col)[:20], border=1, align='C')
                pdf.ln(row_height)
                
                # Linhas com formato de grade
                pdf.set_font("Arial", '', 8)
                for row_idx, row in df.iterrows():
                    for item in row:
                        pdf.cell(col_width, row_height, str(item)[:20], border=1)
                    pdf.ln(row_height)
                
                # Use tempfile para FPDF 1.x para evitar problemas binários
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pdf.output(tmp.name)
                    with open(tmp.name, "rb") as f:
                        pdf_bytes = f.read()
                st.success("Convertido com formato de grade!")
                st.download_button("Baixar PDF", data=pdf_bytes, file_name="planilha.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro: {e}")

elif choice == "Word para PDF":
    st.header("Word para PDF")
    st.warning("Requer Microsoft Word instalado se estiver no Windows (docx2pdf).")
    uploaded_file = st.file_uploader("Envie seu .docx", type=['docx'])
    if uploaded_file:
        if st.button("Converter para PDF"):
            if not docx2pdf_convert:
                st.error("A biblioteca 'docx2pdf' não está instalada.")
            else:
                with st.spinner("Convertendo via MS Word em background..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
                            tmp_docx.write(uploaded_file.getvalue())
                        tmp_pdf = tmp_docx.name.replace(".docx", ".pdf")
                        
                        import pythoncom
                        pythoncom.CoInitialize() # Necessário em Streamlit
                        docx2pdf_convert(tmp_docx.name, tmp_pdf)
                        
                        with open(tmp_pdf, "rb") as f:
                            st.download_button("Baixar PDF", data=f.read(), file_name="documento.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Erro na conversão: {e}")

elif choice == "JPG para PDF":
    st.header("JPG para PDF")
    images_upload = st.file_uploader("Envie sua(s) imagem(ns)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    if images_upload:
        if st.button("Converter"):
            if not Image:
                st.error("Instale 'Pillow' para essa função.")
            else:
                try:
                    imgs = [Image.open(img).convert("RGB") for img in images_upload]
                    output = io.BytesIO()
                    if len(imgs) == 1:
                        imgs[0].save(output, format="PDF")
                    else:
                        imgs[0].save(output, format="PDF", save_all=True, append_images=imgs[1:])
                    st.success("Criado com sucesso!")
                    st.download_button("Baixar PDF", data=output.getvalue(), file_name="imagens.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro: {e}")

# ----------------- 4. CONVERTER DE PDF -----------------
elif choice == "PDF para Excel":
    st.header("PDF para Excel")
    uploaded_file = st.file_uploader("Envie seu PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Converter Múltiplas Tabelas"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(uploaded_file.getbuffer())
                temp_pdf_path = tmp_pdf.name
            with st.spinner("Extraindo..."):
                try:
                    tables = tabula.read_pdf(
                        temp_pdf_path, 
                        pages='all', 
                        multiple_tables=True,
                        encoding='latin-1',
                        java_options="-Dfile.encoding=UTF8",
                        guess=True
                    )
                    if tables:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for i, table in enumerate(tables):
                                table.to_excel(writer, sheet_name=f'Tabela_{i+1}', index=False)
                        st.success(f"{len(tables)} tabela(s) encontrada(s)!")
                        st.download_button("Baixar Excel", data=output.getvalue(), file_name="tabelas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.warning("Nenhuma tabela encontrada no PDF.")
                except Exception as e:
                    st.error(f"Erro (Requer Java instalado): {e}")

elif choice == "PDF para Word":
    st.header("PDF para Word")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Converter para Word"):
            if not Converter:
                st.error("Instale a biblioteca 'pdf2docx'.")
            else:
                with st.spinner("Convertendo (preservando o máximo do fundo e formatação)..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                            tmp_pdf.write(uploaded_file.getvalue())
                        tmp_docx = tmp_pdf.name.replace(".pdf", ".docx")
                        
                        cv = Converter(tmp_pdf.name)
                        cv.convert(tmp_docx)
                        cv.close()
                        
                        with open(tmp_docx, "rb") as f:
                            st.download_button("Baixar DOCX", data=f.read(), file_name="convertido.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except Exception as e:
                        st.error(f"Erro: {e}")

elif choice == "PDF para JPG":
    st.header("PDF para JPG")
    st.info("Utiliza pdf2image. Poppler já está configurado localmente na pasta Downloads.")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Converter Todas as Páginas"):
            if not convert_from_bytes:
                st.error("Instale 'pdf2image' executando: pip install pdf2image")
            else:
                try:
                    # DEFINA O CAMINHO CORRETO PARA A PASTA BIN DO POPPLER
                    import os
                    
                    # Identifica o ambiente: Se for Windows, usa o poppler baixado no modo Local.
                    # Se for Linux (Streamlit Cloud), usa o instalado no sistema via packages.txt
                    if os.name == 'nt':
                        caminho_poppler = r"C:\Users\SEDUC\Downloads\poppler\poppler-24.08.0\Library\bin"
                    else:
                        caminho_poppler = None
                    
                    with st.spinner("Convertendo as páginas, por favor aguarde..."):
                        if caminho_poppler and os.path.exists(caminho_poppler):
                            images = convert_from_bytes(uploaded_file.getvalue(), poppler_path=caminho_poppler)
                        else:
                            images = convert_from_bytes(uploaded_file.getvalue())
                        
                        zip_io = io.BytesIO()
                        with zipfile.ZipFile(zip_io, 'w') as zip_file:
                            for page_num, image in enumerate(images):
                                img_byte_arr = io.BytesIO()
                                image.save(img_byte_arr, format='JPEG', quality=95)
                                zip_file.writestr(f"pagina_{page_num+1}.jpg", img_byte_arr.getvalue())
                        
                        st.success(f"{len(images)} página(s) convertidas!")
                        st.download_button("Baixar ZIP com Imagens", data=zip_io.getvalue(), file_name="paginas_jpg.zip", mime="application/zip")
                except Exception as e:
                    st.error(f"Erro: O 'Poppler' não foi encontrado ou o caminho está incorreto. {e}")

# ----------------- 5. EDITAR -----------------
elif choice == "Rodar PDF":
    st.header("Rodar PDF")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        angle = st.selectbox("Ângulo de rotação", [90, 180, 270])
        if st.button("Aplicar Rotação"):
            reader = PyPDF2.PdfReader(uploaded_file)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            st.success("PDF rotacionado!")
            st.download_button("Baixar", data=output.getvalue(), file_name="rotacionado.pdf", mime="application/pdf")

elif choice == "Numerar Páginas":
    st.header("Numerar Páginas")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        if st.button("Adicionar Numeração (Rodapé Central)"):
            if not canvas:
                st.error("Instale a biblioteca 'reportlab' via requirements.txt")
            else:
                reader = PyPDF2.PdfReader(uploaded_file)
                writer = PyPDF2.PdfWriter()
                for i in range(len(reader.pages)):
                    # Cria pdf temp apenas com o numero
                    out_num = io.BytesIO()
                    c = canvas.Canvas(out_num, pagesize=letter)
                    c.drawString(300, 30, f"Página {i+1}")
                    c.save()
                    out_num.seek(0)
                    num_pdf = PyPDF2.PdfReader(out_num).pages[0]
                    
                    page = reader.pages[i]
                    page.merge_page(num_pdf)
                    writer.add_page(page)
                
                output = io.BytesIO()
                writer.write(output)
                st.success("Páginas numeradas!")
                st.download_button("Baixar", data=output.getvalue(), file_name="numerado.pdf", mime="application/pdf")

elif choice == "Marca d'água":
    st.header("Marca d'água")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    text = st.text_input("Texto da Marca d'água", "CONFIDENCIAL")
    if uploaded_file:
        display_pdf(uploaded_file)
    if uploaded_file and text:
        if st.button("Aplicar Marca d'Água"):
            if not canvas:
                st.error("Instale a biblioteca 'reportlab'.")
            else:
                reader = PyPDF2.PdfReader(uploaded_file)
                writer = PyPDF2.PdfWriter()
                
                # Gera PDF de marca d'agua transparente e diagonal
                out_wm = io.BytesIO()
                c = canvas.Canvas(out_wm, pagesize=letter)
                c.setFont("Helvetica-Bold", 60)
                c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
                c.translate(300, 400)
                c.rotate(45)
                c.drawCentredString(0, 0, text)
                c.save()
                out_wm.seek(0)
                watermark = PyPDF2.PdfReader(out_wm).pages[0]
                
                for page in reader.pages:
                    page.merge_page(watermark)
                    writer.add_page(page)
                    
                output = io.BytesIO()
                writer.write(output)
                st.success("Marca d'água aplicada!")
                st.download_button("Baixar", data=output.getvalue(), file_name="marca_dagua.pdf", mime="application/pdf")

elif choice == "Editar Texto":
    st.header("Anotação / Texto Personalizado")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    if uploaded_file:
        display_pdf(uploaded_file)
        texto = st.text_input("Texto para adicionar na primeira página")
        x = st.slider("Posição X (Horizontal)", 0, 800, 100)
        y = st.slider("Posição Y (Vertical)", 0, 800, 700)
        if st.button("Inserir Anotação"):
            if not canvas:
                st.error("Requer 'reportlab'.")
            else:
                reader = PyPDF2.PdfReader(uploaded_file)
                writer = PyPDF2.PdfWriter()
                
                out_txt = io.BytesIO()
                c = canvas.Canvas(out_txt, pagesize=letter)
                c.setFont("Helvetica", 14)
                c.drawString(x, y, texto)
                c.save()
                out_txt.seek(0)
                txt_pdf = PyPDF2.PdfReader(out_txt).pages[0]
                
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    if i == 0:
                        page.merge_page(txt_pdf)
                    writer.add_page(page)
                
                output = io.BytesIO()
                writer.write(output)
                st.success("Texto adicionado!")
                st.download_button("Baixar", data=output.getvalue(), file_name="anotado.pdf", mime="application/pdf")

# ----------------- 6. SEGURANÇA -----------------
elif choice == "Proteger PDF":
    st.header("Proteger PDF")
    uploaded_file = st.file_uploader("Envie o PDF", type='pdf')
    senha = st.text_input("Senha", type="password")
    if uploaded_file:
        display_pdf(uploaded_file)
    if uploaded_file and senha:
        if st.button("Criptografar PDF"):
            reader = PyPDF2.PdfReader(uploaded_file)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(senha)
            output = io.BytesIO()
            writer.write(output)
            st.success("PDF protegido por senha!")
            st.download_button("Baixar Protegido", data=output.getvalue(), file_name="protegido.pdf", mime="application/pdf")

elif choice == "Desbloquear PDF":
    st.header("Desbloquear PDF")
    uploaded_file = st.file_uploader("Envie o PDF protegido", type='pdf')
    senha = st.text_input("Senha atual para remover proteção", type="password")
    if uploaded_file:
        display_pdf(uploaded_file)
    if uploaded_file and senha:
        if st.button("Remover Senha"):
            reader = PyPDF2.PdfReader(uploaded_file)
            if reader.is_encrypted:
                try:
                    reader.decrypt(senha)
                    writer = PyPDF2.PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    output = io.BytesIO()
                    writer.write(output)
                    st.success("Senha removida!")
                    st.download_button("Baixar Desbloqueado", data=output.getvalue(), file_name="desbloqueado.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro: Senha incorreta ou arquivo inválido. {e}")
            else:
                st.info("Esse arquivo já está sem senha.")
