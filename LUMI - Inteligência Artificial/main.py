
import os
import json
import time
import threading
import hashlib
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

FUNDO = "#0B1020"
PAINEL = "#111A30"
CAMPO = "#1B2542"
ROXO = "#8B7CFF"
CIANO = "#55E6FF"
BRANCO = "#F2F5FF"
CINZA = "#A5B0CC"
ARQUIVO_USUARIOS = "usuarios.json"

janela = tk.Tk()
janela.title("LUMI | Inteligência Artificial")
janela.geometry("1000x700")
janela.minsize(750, 550)
janela.configure(bg=FUNDO)

cliente = None
conversa = None
tema_escuro = True
ocupado = False
area_mensagens = None
canvas_mensagens = None
campo_mensagem = None
botao_enviar = None
status_label = None
usuario_atual = "Usuário"


def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}

    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados if isinstance(dados, dict) else {}
    except (json.JSONDecodeError, OSError):
        messagebox.showerror(
            "Erro nos cadastros",
            "Não foi possível ler o arquivo usuarios.json."
        )
        return {}


def salvar_usuarios(usuarios):
    try:
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)
        return True
    except OSError as erro:
        messagebox.showerror(
            "Erro ao salvar",
            f"Não foi possível salvar o cadastro:\n{erro}"
        )
        return False


def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def criar_conversa():
    global conversa

    conversa = cliente.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "Seu nome é LUMI. Você é uma assistente virtual amigável, "
                "educada, inteligente e atenciosa. Responda sempre em "
                "português do Brasil, com linguagem natural e clara. "
                "Converse sobre assuntos gerais, incluindo curiosidades, "
                "filmes, séries, músicas, receitas, culinária, viagens, "
                "cultura, história, ciência, saúde geral, tecnologia, "
                "programação, estudos, trabalho e situações do dia a dia. "
                "Não limite suas respostas a assuntos escolares ou tecnologia. "
                "Adapte o tamanho da resposta à pergunta do usuário. "
                "Seja respeitosa, acolhedora e evite respostas complicadas."
            )
        )
    )


def limpar_tela():
    for widget in janela.winfo_children():
        widget.destroy()


def entrar():
    usuario = entrada_usuario.get().strip()
    senha = entrada_senha.get()
    usuarios = carregar_usuarios()

    if usuario == "admin" and senha == "1234":
        abrir_chat(usuario)
    elif usuario in usuarios and usuarios[usuario] == hash_senha(senha):
        abrir_chat(usuario)
    else:
        messagebox.showerror(
            "Acesso negado",
            "Usuário ou senha incorretos."
        )


def cadastrar():
    nome = entrada_nome.get().strip()
    usuario = entrada_novo_usuario.get().strip()
    senha = entrada_nova_senha.get()
    confirmar = entrada_confirmar_senha.get()

    if not nome or not usuario or not senha or not confirmar:
        messagebox.showwarning(
            "Campos obrigatórios",
            "Preencha todos os campos."
        )
        return

    if len(usuario) < 3:
        messagebox.showwarning(
            "Usuário inválido",
            "O nome de usuário deve ter pelo menos 3 caracteres."
        )
        return

    if len(senha) < 4:
        messagebox.showwarning(
            "Senha inválida",
            "A senha deve ter pelo menos 4 caracteres."
        )
        return

    if senha != confirmar:
        messagebox.showerror(
            "Senhas diferentes",
            "A confirmação da senha não corresponde."
        )
        return

    usuarios = carregar_usuarios()

    if usuario.lower() == "admin" or any(
        existente.lower() == usuario.lower()
        for existente in usuarios
    ):
        messagebox.showerror(
            "Usuário já existe",
            "Escolha outro nome de usuário."
        )
        return

    usuarios[usuario] = hash_senha(senha)

    if salvar_usuarios(usuarios):
        messagebox.showinfo(
            "Cadastro concluído",
            f"Conta criada com sucesso, {nome}!"
        )
        tela_login(usuario)


def tela_login(usuario_inicial=""):
    limpar_tela()
    janela.configure(bg=FUNDO)

    principal = tk.Frame(janela, bg=FUNDO)
    principal.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        principal,
        text="🤖 LUMI",
        font=("Segoe UI", 38, "bold"),
        fg=CIANO,
        bg=FUNDO
    ).pack()

    tk.Label(
        principal,
        text="INTELIGÊNCIA ARTIFICIAL",
        font=("Segoe UI", 10, "bold"),
        fg=ROXO,
        bg=FUNDO
    ).pack(pady=(0, 25))

    cartao = tk.Frame(
        principal,
        bg=PAINEL,
        padx=35,
        pady=30,
        highlightbackground=ROXO,
        highlightthickness=1
    )
    cartao.pack()

    tk.Label(
        cartao,
        text="Acesse sua conta",
        font=("Segoe UI", 17, "bold"),
        fg=BRANCO,
        bg=PAINEL
    ).pack(pady=(0, 20))

    tk.Label(
        cartao,
        text="NOME DE USUÁRIO",
        font=("Segoe UI", 9, "bold"),
        fg=CIANO,
        bg=PAINEL
    ).pack(anchor="w")

    global entrada_usuario, entrada_senha

    entrada_usuario = tk.Entry(
        cartao,
        font=("Segoe UI", 12),
        bg=CAMPO,
        fg=BRANCO,
        insertbackground=BRANCO,
        relief="flat",
        width=30
    )
    entrada_usuario.pack(ipady=9, pady=(5, 15))
    entrada_usuario.insert(0, usuario_inicial)

    tk.Label(
        cartao,
        text="SENHA",
        font=("Segoe UI", 9, "bold"),
        fg=CIANO,
        bg=PAINEL
    ).pack(anchor="w")

    entrada_senha = tk.Entry(
        cartao,
        font=("Segoe UI", 12),
        bg=CAMPO,
        fg=BRANCO,
        insertbackground=BRANCO,
        show="*",
        relief="flat",
        width=30
    )
    entrada_senha.pack(ipady=9, pady=(5, 20))
    entrada_senha.bind("<Return>", lambda evento: entrar())

    tk.Button(
        cartao,
        text="ENTRAR NO SISTEMA",
        command=entrar,
        font=("Segoe UI", 10, "bold"),
        bg=ROXO,
        fg=BRANCO,
        activebackground=CIANO,
        activeforeground=FUNDO,
        relief="flat",
        cursor="hand2"
    ).pack(fill="x", ipady=10)

    tk.Button(
        cartao,
        text="CRIAR UMA CONTA",
        command=tela_cadastro,
        font=("Segoe UI", 10, "bold"),
        bg=CAMPO,
        fg=CIANO,
        activebackground=ROXO,
        relief="flat",
        cursor="hand2"
    ).pack(fill="x", ipady=9, pady=(10, 0))

    tk.Label(
        principal,
        text="SISTEMA LUMI • CONEXÃO INTELIGENTE",
        font=("Segoe UI", 9),
        fg=CINZA,
        bg=FUNDO
    ).pack(pady=20)

    entrada_usuario.focus_set()
    janela.bind("<Return>", lambda evento: entrar())


def tela_cadastro():
    limpar_tela()
    janela.configure(bg=FUNDO)

    principal = tk.Frame(janela, bg=FUNDO)
    principal.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        principal,
        text="✨ LUMI",
        font=("Segoe UI", 34, "bold"),
        fg=CIANO,
        bg=FUNDO
    ).pack()

    tk.Label(
        principal,
        text="CRIE SUA CONTA",
        font=("Segoe UI", 10, "bold"),
        fg=ROXO,
        bg=FUNDO
    ).pack(pady=(0, 20))

    cartao = tk.Frame(
        principal,
        bg=PAINEL,
        padx=32,
        pady=24,
        highlightbackground=ROXO,
        highlightthickness=1
    )
    cartao.pack()

    def criar_campo(rotulo, esconder=False):
        tk.Label(
            cartao,
            text=rotulo,
            font=("Segoe UI", 9, "bold"),
            fg=CIANO,
            bg=PAINEL
        ).pack(anchor="w")

        entrada = tk.Entry(
            cartao,
            font=("Segoe UI", 11),
            bg=CAMPO,
            fg=BRANCO,
            insertbackground=BRANCO,
            relief="flat",
            width=32,
            show="*" if esconder else ""
        )
        entrada.pack(ipady=8, pady=(4, 12))
        return entrada

    global entrada_nome
    global entrada_novo_usuario
    global entrada_nova_senha
    global entrada_confirmar_senha

    entrada_nome = criar_campo("SEU NOME")
    entrada_novo_usuario = criar_campo("NOME DE USUÁRIO")
    entrada_nova_senha = criar_campo("SENHA", True)
    entrada_confirmar_senha = criar_campo("CONFIRME A SENHA", True)

    entrada_confirmar_senha.bind(
        "<Return>",
        lambda evento: cadastrar()
    )

    tk.Button(
        cartao,
        text="CADASTRAR",
        command=cadastrar,
        font=("Segoe UI", 10, "bold"),
        bg=ROXO,
        fg=BRANCO,
        activebackground=CIANO,
        relief="flat",
        cursor="hand2"
    ).pack(fill="x", ipady=9, pady=(4, 8))

    tk.Button(
        cartao,
        text="VOLTAR AO LOGIN",
        command=tela_login,
        font=("Segoe UI", 10, "bold"),
        bg=CAMPO,
        fg=CIANO,
        activebackground=ROXO,
        relief="flat",
        cursor="hand2"
    ).pack(fill="x", ipady=8)

    tk.Label(
        principal,
        text="Seus dados ficam salvos neste computador.",
        font=("Segoe UI", 9),
        fg=CINZA,
        bg=FUNDO
    ).pack(pady=14)

    entrada_nome.focus_set()
    janela.unbind("<Return>")


def adicionar_mensagem(remetente, texto, usuario=False):
    if usuario:
        cor_fundo = "#1B3150" if tema_escuro else "#E0E7FF"
        icone = "👤"
        alinhamento = "e"
        cor_nome = CIANO if tema_escuro else "#2456A6"
    else:
        cor_fundo = "#26304A" if tema_escuro else "#F0EAFB"
        icone = "🤖"
        alinhamento = "w"
        cor_nome = ROXO if tema_escuro else "#6941C6"

    cor_texto = BRANCO if tema_escuro else "#182033"

    linha = tk.Frame(
        area_mensagens,
        bg=PAINEL,
        padx=12,
        pady=7
    )
    linha.pack(fill="x")

    caixa = tk.Frame(
        linha,
        bg=cor_fundo,
        padx=14,
        pady=11,
        highlightbackground=cor_nome,
        highlightthickness=1
    )
    caixa.pack(anchor=alinhamento, padx=5)

    tk.Label(
        caixa,
        text=f"{icone}  {remetente}",
        font=("Segoe UI", 9, "bold"),
        fg=cor_nome,
        bg=cor_fundo
    ).pack(anchor="w")

    tk.Label(
        caixa,
        text=texto,
        font=("Segoe UI", 11),
        fg=cor_texto,
        bg=cor_fundo,
        wraplength=600,
        justify="left"
    ).pack(anchor="w", pady=(5, 0))

    canvas_mensagens.update_idletasks()
    canvas_mensagens.configure(
        scrollregion=canvas_mensagens.bbox("all")
    )
    canvas_mensagens.yview_moveto(1)


def resposta_recebida(texto, erro=False):
    global ocupado

    if status_label.winfo_exists():
        status_label.config(
            text="ERRO NA CONEXÃO" if erro else "SISTEMA ONLINE",
            fg="#FF7A90" if erro else CIANO
        )

    adicionar_mensagem("LUMI", texto)
    ocupado = False
    campo_mensagem.config(state="normal")
    botao_enviar.config(state="normal")
    campo_mensagem.focus_set()


def consultar_gemini(texto):
    try:
        time.sleep(0.5)
        resposta = conversa.send_message(message=texto)
        conteudo = resposta.text or "Não consegui gerar uma resposta."
        janela.after(
            0,
            lambda: resposta_recebida(conteudo)
        )
    except Exception as erro:
        detalhe = str(erro)

        if "503" in detalhe or "UNAVAILABLE" in detalhe:
            mensagem = (
                "O Gemini está recebendo muitas solicitações no momento. "
                "Aguarde um pouco e tente novamente."
            )
        elif "429" in detalhe or "RESOURCE_EXHAUSTED" in detalhe:
            mensagem = (
                "O limite de solicitações da API foi atingido. "
                "Aguarde um pouco antes de tentar novamente."
            )
        else:
            mensagem = (
                "Não consegui me conectar ao Gemini. "
                "Confira a internet e a configuração da API."
            )

        janela.after(
            0,
            lambda msg=mensagem: resposta_recebida(msg, True)
        )


def enviar_mensagem(evento=None):
    global ocupado

    texto = campo_mensagem.get().strip()

    if not texto or ocupado:
        return

    campo_mensagem.delete(0, "end")
    adicionar_mensagem(usuario_atual, texto, True)

    ocupado = True
    campo_mensagem.config(state="disabled")
    botao_enviar.config(state="disabled")
    status_label.config(
        text="LUMI ESTÁ PENSANDO...",
        fg=ROXO
    )

    threading.Thread(
        target=consultar_gemini,
        args=(texto,),
        daemon=True
    ).start()


def limpar_conversa():
    if ocupado:
        messagebox.showinfo(
            "Aguarde",
            "Espere a LUMI terminar a resposta antes de limpar."
        )
        return

    for widget in area_mensagens.winfo_children():
        widget.destroy()

    criar_conversa()
    adicionar_mensagem(
        "LUMI",
        "Conversa reiniciada! Sobre o que vamos conversar?"
    )


def trocar_tema():
    global tema_escuro

    tema_escuro = not tema_escuro

    if tema_escuro:
        cor_fundo = FUNDO
        cor_painel = PAINEL
        cor_texto = BRANCO
        cor_campo = CAMPO
    else:
        cor_fundo = "#F2F4FA"
        cor_painel = "#FFFFFF"
        cor_texto = "#182033"
        cor_campo = "#E5E7F0"

    janela.configure(bg=cor_fundo)

    for widget in janela.winfo_children():
        atualizar_cores(
            widget,
            cor_fundo,
            cor_painel,
            cor_texto,
            cor_campo
        )


def atualizar_cores(widget, fundo, painel, texto, campo):
    try:
        if widget == area_mensagens or widget == canvas_mensagens:
            widget.configure(bg=painel)
        elif widget == campo_mensagem:
            widget.configure(
                bg=campo,
                fg=texto,
                insertbackground=texto
            )
        elif isinstance(widget, tk.Button):
            if widget.cget("text") == "ENVIAR":
                widget.configure(bg=ROXO, fg=BRANCO)
            elif widget.cget("text") == "SAIR DA CONTA":
                widget.configure(bg=painel, fg="#FF7A90")
            else:
                widget.configure(bg=painel, fg=texto)
        elif isinstance(widget, tk.Label):
            if widget == status_label:
                widget.configure(bg=painel)
            elif "LUMI" in widget.cget("text"):
                widget.configure(bg=fundo, fg=CIANO)
            else:
                widget.configure(bg=painel, fg=texto)
        else:
            widget.configure(bg=painel)
    except tk.TclError:
        pass

    for filho in widget.winfo_children():
        atualizar_cores(
            filho,
            fundo,
            painel,
            texto,
            campo
        )


def sair_da_conta():
    global cliente, conversa, ocupado

    if ocupado:
        messagebox.showinfo(
            "Aguarde",
            "Espere a LUMI terminar a resposta antes de sair."
        )
        return

    resposta = messagebox.askyesno(
        "Sair da conta",
        "Deseja sair da sua conta e voltar para o login?"
    )

    if resposta:
        cliente = None
        conversa = None
        tela_login()


def abrir_chat(usuario):
    global cliente, usuario_atual
    global area_mensagens, canvas_mensagens
    global campo_mensagem, botao_enviar, status_label

    usuario_atual = usuario

    if not API_KEY:
        messagebox.showerror(
            "Chave não encontrada",
            "Confira se o arquivo .env contém GEMINI_API_KEY com sua chave."
        )
        return

    try:
        cliente = genai.Client(api_key=API_KEY)
        criar_conversa()
    except Exception as erro:
        messagebox.showerror(
            "Erro ao iniciar",
            f"Não consegui preparar a conexão:\n{erro}"
        )
        return

    janela.unbind("<Return>")
    limpar_tela()
    janela.configure(bg=FUNDO)

    topo = tk.Frame(
        janela,
        bg=PAINEL,
        padx=20,
        pady=14
    )
    topo.pack(fill="x")

    tk.Label(
        topo,
        text="🤖 LUMI",
        font=("Segoe UI", 22, "bold"),
        fg=CIANO,
        bg=PAINEL
    ).pack(side="left")

    tk.Label(
        topo,
        text="INTELIGÊNCIA ARTIFICIAL",
        font=("Segoe UI", 9, "bold"),
        fg=ROXO,
        bg=PAINEL
    ).pack(side="left", padx=15, pady=(7, 0))

    tk.Button(
        topo,
        text="SAIR DA CONTA",
        command=sair_da_conta,
        bg=CAMPO,
        fg="#FF7A90",
        activebackground=ROXO,
        relief="flat",
        cursor="hand2"
    ).pack(side="right", padx=5)

    tk.Button(
        topo,
        text="TROCAR TEMA",
        command=trocar_tema,
        bg=CAMPO,
        fg=BRANCO,
        relief="flat",
        cursor="hand2"
    ).pack(side="right", padx=5)

    tk.Button(
        topo,
        text="LIMPAR",
        command=limpar_conversa,
        bg=CAMPO,
        fg=BRANCO,
        relief="flat",
        cursor="hand2"
    ).pack(side="right", padx=5)

    status_label = tk.Label(
        janela,
        text="SISTEMA ONLINE",
        font=("Segoe UI", 9, "bold"),
        fg=CIANO,
        bg=FUNDO,
        anchor="w",
        padx=20,
        pady=8
    )
    status_label.pack(fill="x")

    quadro_chat = tk.Frame(janela, bg=PAINEL)
    quadro_chat.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=8
    )

    canvas_mensagens = tk.Canvas(
        quadro_chat,
        bg=PAINEL,
        highlightthickness=0
    )

    barra = tk.Scrollbar(
        quadro_chat,
        orient="vertical",
        command=canvas_mensagens.yview
    )

    area_mensagens = tk.Frame(
        canvas_mensagens,
        bg=PAINEL
    )

    janela_canvas = canvas_mensagens.create_window(
        (0, 0),
        window=area_mensagens,
        anchor="nw"
    )

    area_mensagens.bind(
        "<Configure>",
        lambda evento: canvas_mensagens.configure(
            scrollregion=canvas_mensagens.bbox("all")
        )
    )

    canvas_mensagens.bind(
        "<Configure>",
        lambda evento: canvas_mensagens.itemconfigure(
            janela_canvas,
            width=evento.width
        )
    )

    canvas_mensagens.configure(
        yscrollcommand=barra.set
    )
    canvas_mensagens.pack(
        side="left",
        fill="both",
        expand=True
    )
    barra.pack(side="right", fill="y")

    rodape = tk.Frame(
        janela,
        bg=FUNDO,
        padx=18,
        pady=14
    )
    rodape.pack(fill="x")

    campo_mensagem = tk.Entry(
        rodape,
        font=("Segoe UI", 12),
        bg=CAMPO,
        fg=BRANCO,
        insertbackground=BRANCO,
        relief="flat"
    )
    campo_mensagem.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=12,
        padx=(0, 10)
    )
    campo_mensagem.bind("<Return>", enviar_mensagem)

    botao_enviar = tk.Button(
        rodape,
        text="ENVIAR",
        command=enviar_mensagem,
        font=("Segoe UI", 10, "bold"),
        bg=ROXO,
        fg=BRANCO,
        activebackground=CIANO,
        relief="flat",
        cursor="hand2",
        padx=22
    )
    botao_enviar.pack(side="right", ipady=8)

    adicionar_mensagem(
        "LUMI",
        f"Olá, {usuario}! ✨ Sou a LUMI, sua assistente virtual. "
        "Podemos conversar sobre qualquer assunto: curiosidades, "
        "filmes, música, receitas, viagens, tecnologia, estudos "
        "e muito mais. O que você gostaria de saber?"
    )

    campo_mensagem.focus_set()


tela_login()
janela.mainloop()

