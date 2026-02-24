# CONVERTPDF 📄

Este é um web app local criado com Streamlit, replicando ferramentas úteis de PDF (estilo iLovePDF).

## Funcionalidades
- **Juntar PDF**: Combine vários PDFs em um só.
- **Dividir PDF**: Extraia páginas específicas.
- **Comprimir PDF**: Reduza o tamanho do seu PDF localmente.
- **PDF para Excel**: Converta tabelas de um PDF em formato `.xlsx` estruturado.
- **Excel para PDF**: Converta planilhas em um documento PDF.

## Imagem de Fundo (Abstrata / Rede Neural)
Se você tem a imagem `rede neural abstrata azul brilhante`:
1. Salve ela na mesma pasta deste arquivo `app.py`.
2. Renomeie o arquivo de imagem para **`background.jpg`** ou **`background.png`**.
3. O app carregará sua imagem como plano de fundo de tela cheia automaticamente. Se não houver arquivo, ele exibirá um fundo estilizado gerado via CSS (gradiente escuro com pontos luminosos azuis).

---

## 🚀 Setup e Instalação

### Passo 1: Instale as bibliotecas Python
Abra o terminal (Prompt de Comando ou PowerShell) na pasta do projeto e execute:
```bash
pip install streamlit PyPDF2 pandas openpyxl tabula-py fpdf2
```
> **Nota Opcional:** Você também pode instalar usando `fpdf` antigo, mas o código atual funciona muito bem com `fpdf` ou `fpdf2` atualizados.

### Passo 2: Instalar o Java Development Kit (JDK)
A extração de tabelas de PDF para Excel (via **Tabula-py**) só funciona se o Java (JDK) estiver instalado no seu Windows:
1. Acesse o site oficial de download da Oracle ou Eclipse Adoptium (temos preferência pelo [Adoptium Temurin JDK](https://adoptium.net/pt-BR/)).
2. Baixe o instalador `.msi` mais recente (Java 17 ou 21).
3. **MUITO IMPORTANTE:** Durante a instalação, clique na opção "Set or Add JAVA_HOME variable" e marque para **"Installed on local hard drive"** (Adicionar ao PATH).
4. Siga até o fim. Depois de concluído, você deve ser capaz de abrir um novo Terminal e digitar `java -version` para ver a versão.

### Passo 3: Rodar o Aplicativo
Assim que as instalações acabarem, digite no terminal (ainda dentro da pasta do projeto):
```bash
streamlit run app.py
```
O navegador abrirá automaticamente com o seu **CONVERTPDF** rodando!

---
Desenvolvido via Agente IA (Antigravity).
