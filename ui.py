# ui.py
"""
Interface gráfica principal usando CustomTkinter.
"""
import customtkinter as ctk
from database import init_db, inserir_usuario, get_connection
import csv
from tkinter import filedialog, messagebox

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_login_success = on_login_success
        self.usuario_var = ctk.StringVar()
        self.senha_var = ctk.StringVar()
        ctk.CTkLabel(self, text="Login", font=("Arial", 22)).pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.usuario_var, placeholder_text="Usuário").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.senha_var, placeholder_text="Senha", show="*").pack(pady=5)
        self.msg = ctk.CTkLabel(self, text="", text_color="red")
        self.msg.pack()
        ctk.CTkButton(self, text="Entrar", command=self.login).pack(pady=10)
        ctk.CTkButton(self, text="Cadastrar novo usuário", command=self.cadastrar).pack(pady=2)

    def login(self):
        usuario = self.usuario_var.get().strip()
        senha = self.senha_var.get().strip()
        if not usuario or not senha:
            self.msg.configure(text="Preencha todos os campos.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE usuario=%s AND senha=%s", (usuario, senha))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            self.on_login_success(user[0], usuario)
        else:
            self.msg.configure(text="Usuário ou senha inválidos.")

    def cadastrar(self):
        usuario = self.usuario_var.get().strip()
        senha = self.senha_var.get().strip()
        if not usuario or not senha:
            self.msg.configure(text="Preencha todos os campos.")
            return
        try:
            inserir_usuario(usuario, senha)
            self.msg.configure(text="Usuário cadastrado! Faça login.", text_color="green")
        except Exception as e:
            self.msg.configure(text="Erro ao cadastrar: " + str(e), text_color="red")

class MainApp(ctk.CTk):
    def clear_main(self):
        """
        Remove todos os widgets da janela principal, exceto o frame de login (se existir).
        """
        for widget in self.winfo_children():
            if not isinstance(widget, LoginFrame):
                widget.destroy()
    def __init__(self):
        super().__init__()
        self.title("Finanças Pessoais")
        self.geometry("900x600")
        self.resizable(False, False)
        self.usuario_id = None
        self.usuario_nome = None
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.pack(expand=True)

    def on_login_success(self, usuario_id, usuario_nome):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.login_frame.pack_forget()
        self.verificar_notificacoes()
        self.show_dashboard()

    def verificar_notificacoes(self):
        # Notificação: gasto maior em categoria do que mês anterior
        from database import get_connection, inserir_notificacao, buscar_notificacoes, marcar_notificacao_lida
        import datetime
        conn = get_connection()
        cur = conn.cursor()
        hoje = datetime.date.today()
        mes_ini = hoje.replace(day=1)
        mes_ant = (mes_ini - datetime.timedelta(days=1)).replace(day=1)
        # Para cada categoria de gasto
        cur.execute("""
            SELECT c.id, c.nome FROM categorias c WHERE c.tipo='gasto'
        """)
        cats = cur.fetchall()
        for cat_id, cat_nome in cats:
            # Total mês atual
            cur.execute("""
                SELECT COALESCE(SUM(valor),0) FROM lancamentos
                WHERE usuario_id=%s AND tipo='gasto' AND categoria_id=%s AND data >= %s
            """, (self.usuario_id, cat_id, mes_ini))
            atual = float(cur.fetchone()[0])
            # Total mês anterior
            cur.execute("""
                SELECT COALESCE(SUM(valor),0) FROM lancamentos
                WHERE usuario_id=%s AND tipo='gasto' AND categoria_id=%s AND data >= %s AND data < %s
            """, (self.usuario_id, cat_id, mes_ant, mes_ini))
            anterior = float(cur.fetchone()[0])
            if anterior > 0 and atual > anterior:
                msg = f"Você gastou mais com {cat_nome} este mês (R$ {atual:.2f}) do que no mês passado (R$ {anterior:.2f})!"
                inserir_notificacao(self.usuario_id, msg)
        cur.close()
        conn.close()

    def show_dashboard_content(self):
        """
        Exibe o dashboard principal com saudação, notificações, totais e dicas rotativas.
        Layout responsivo e organizado.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # Saudação
        ctk.CTkLabel(self.main_frame, text=f"Bem-vindo, {self.usuario_nome}", font=("Arial", 20, "bold")).pack(pady=10)
        # Notificações
        self.exibir_notificacoes()
        # TOTAIS em linha
        saldo, total_gastos, total_invest = self.get_dashboard_totals()
        totais_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        totais_frame.pack(pady=5)
        ctk.CTkLabel(totais_frame, text=f"Saldo atual: R$ {saldo:.2f}", font=("Arial", 16)).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(totais_frame, text=f"Total de gastos no mês: R$ {total_gastos:.2f}", font=("Arial", 14)).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(totais_frame, text=f"Total de investimentos: R$ {total_invest:.2f}", font=("Arial", 14)).grid(row=0, column=2, padx=10)
        # Dicas rotativas
        from tips import get_tips
        self.tips = get_tips()
        self.tip_label = ctk.CTkLabel(self.main_frame, text=self.tips[0], font=("Arial", 13, "italic"), text_color="#0077cc")
        self.tip_label.pack(pady=15)
        self.tip_index = 0
        self.after(4000, self.rotate_tip)

    def exibir_notificacoes(self):
        from database import buscar_notificacoes, marcar_notificacao_lida
        notifs = buscar_notificacoes(self.usuario_id)
        if notifs:
            for notif in notifs:
                frame = ctk.CTkFrame(self.main_frame, fg_color="#ffe9b3")
                frame.pack(pady=2, padx=10, fill="x")
                ctk.CTkLabel(frame, text=notif[1], text_color="#b36b00").pack(side="left", padx=8)
                ctk.CTkButton(frame, text="OK", width=40, command=lambda n=notif[0]: self.ler_notificacao(n)).pack(side="right", padx=8)

    def ler_notificacao(self, notif_id):
        from database import marcar_notificacao_lida
        marcar_notificacao_lida(notif_id)
        self.show_dashboard_content()


    def show_dashboard(self):
        self.clear_main()
        self.menu = MenuLateral(self, self.on_menu_select)
        self.menu.pack(side="left", fill="y")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both")
        self.show_dashboard_content()


    def get_dashboard_totals(self):
        from database import get_connection
        import datetime
        conn = get_connection()
        cur = conn.cursor()
        # Total gastos mês
        hoje = datetime.date.today()
        mes_ini = hoje.replace(day=1)
        cur.execute("""
            SELECT COALESCE(SUM(valor),0) FROM lancamentos
            WHERE usuario_id=%s AND tipo='gasto' AND data >= %s
        """, (self.usuario_id, mes_ini))
        total_gastos = float(cur.fetchone()[0])
        # Total investimentos
        cur.execute("""
            SELECT COALESCE(SUM(valor),0) FROM lancamentos
            WHERE usuario_id=%s AND tipo='investimento'
        """, (self.usuario_id,))
        total_invest = float(cur.fetchone()[0])
        # Saldo = investimentos - gastos
        saldo = total_invest - total_gastos
        cur.close()
        conn.close()
        return saldo, total_gastos, total_invest

    def rotate_tip(self):
        if hasattr(self, 'tips'):
            self.tip_index = (self.tip_index + 1) % len(self.tips)
            self.tip_label.configure(text=self.tips[self.tip_index])
            self.after(4000, self.rotate_tip)

    def on_menu_select(self, menu):
        if menu == "Dashboard":
            self.show_dashboard_content()
        elif menu == "Lançamentos":
            self.show_lancamentos()
        elif menu == "Objetivos":
            self.show_objetivos()
        elif menu == "Orçamento":
            self.show_orcamento()
        elif menu == "Relatórios":
            self.show_relatorios()
        elif menu == "Configurações":
            self.show_configuracoes()
        elif menu == "Sair":
            self.logout()

    def show_orcamento(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.main_frame, text="Orçamento Mensal", font=("Arial", 18)).pack(pady=10)
        OrcamentoForm(self.main_frame, self.usuario_id, self.refresh_orcamento).pack(pady=8)
        self.orcamento_list_frame = ctk.CTkFrame(self.main_frame)
        self.orcamento_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_orcamento()

    def refresh_orcamento(self):
        for widget in self.orcamento_list_frame.winfo_children():
            widget.destroy()
        from database import buscar_orcamento, buscar_categorias, get_connection
        import datetime
        mes_ano = datetime.date.today().strftime("%Y-%m")
        orcs = buscar_orcamento(self.usuario_id, mes_ano)
        cats = {c[0]: c[1] for c in buscar_categorias()}
        # Buscar gastos reais por categoria
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT categoria_id, SUM(valor) FROM lancamentos
            WHERE usuario_id=%s AND tipo='gasto' AND DATE_FORMAT(data, '%%Y-%%m')=%s
            GROUP BY categoria_id
        """, (self.usuario_id, mes_ano))
        gastos = dict(cur.fetchall())
        cur.close()
        conn.close()
        if not orcs:
            ctk.CTkLabel(self.orcamento_list_frame, text="Nenhum orçamento cadastrado para este mês.").pack()
            return
        for cat_id, valor_planejado in orcs:
            nome = cats.get(cat_id, "?")
            gasto_real = gastos.get(cat_id, 0)
            alerta = " (ALERTA!)" if gasto_real > valor_planejado else ""
            ctk.CTkLabel(self.orcamento_list_frame, text=f"{nome}: Limite R$ {valor_planejado:.2f} | Gasto: R$ {gasto_real:.2f}{alerta}").pack(anchor="w", padx=8, pady=2)

# Formulário de orçamento
class OrcamentoForm(ctk.CTkFrame):
    def __init__(self, master, usuario_id, on_save, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_id = usuario_id
        self.on_save = on_save
        self.categoria_var = ctk.StringVar()
        self.valor_var = ctk.StringVar()
        self.mes_var = ctk.StringVar()
        from database import buscar_categorias
        cats = buscar_categorias("gasto")
        nomes = [c[1] for c in cats] if cats else [""]
        self.cat_map = {c[1]: c[0] for c in cats}
        ctk.CTkLabel(self, text="Categoria:").grid(row=0, column=0, padx=2)
        ctk.CTkOptionMenu(self, variable=self.categoria_var, values=nomes).grid(row=0, column=1, padx=2)
        ctk.CTkLabel(self, text="Limite (R$):").grid(row=0, column=2, padx=2)
        ctk.CTkEntry(self, textvariable=self.valor_var, width=80).grid(row=0, column=3, padx=2)
        ctk.CTkLabel(self, text="Mês (AAAA-MM):").grid(row=1, column=0, padx=2)
        ctk.CTkEntry(self, textvariable=self.mes_var, width=80).grid(row=1, column=1, padx=2)
        self.msg = ctk.CTkLabel(self, text="", text_color="red")
        self.msg.grid(row=2, column=0, columnspan=4)
        ctk.CTkButton(self, text="Salvar orçamento", command=self.salvar).grid(row=3, column=0, columnspan=4, pady=4)

    def salvar(self):
        from database import inserir_orcamento
        cat_nome = self.categoria_var.get()
        valor = self.valor_var.get().replace(",", ".")
        mes = self.mes_var.get().strip()
        if not (cat_nome and valor and mes):
            self.msg.configure(text="Preencha todos os campos.")
            return
        try:
            valor = float(valor)
        except ValueError:
            self.msg.configure(text="Valor inválido.")
            return
        cat_id = self.cat_map.get(cat_nome)
        if not cat_id:
            self.msg.configure(text="Categoria inválida.")
            return
        try:
            inserir_orcamento(self.usuario_id, cat_id, mes, valor)
            self.msg.configure(text="Orçamento salvo!", text_color="green")
            self.on_save()
        except Exception as e:
            self.msg.configure(text="Erro: " + str(e), text_color="red")

    def show_objetivos(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.main_frame, text="Sonhos / Objetivos Financeiros", font=("Arial", 18)).pack(pady=10)
        ObjetivoForm(self.main_frame, self.usuario_id, self).pack(pady=8)
        self.objetivos_list_frame = ctk.CTkFrame(self.main_frame)
        self.objetivos_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_objetivos()

    def refresh_objetivos(self):
        for widget in self.objetivos_list_frame.winfo_children():
            widget.destroy()
        from database import buscar_objetivos
        objetivos = buscar_objetivos(self.usuario_id)
        if not objetivos:
            ctk.CTkLabel(self.objetivos_list_frame, text="Nenhum objetivo cadastrado.").pack()
            return
        for obj in objetivos:
            nome, meta, atual, prazo, prioridade, desc = obj[1], obj[2], obj[3], obj[4], obj[5], obj[6]
            progresso = (float(atual)/float(meta)*100) if meta else 0
            frame = ctk.CTkFrame(self.objetivos_list_frame)
            frame.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(frame, text=f"{nome} (Meta: R$ {meta:.2f})", font=("Arial", 14, "bold")).pack(anchor="w")
            ctk.CTkLabel(frame, text=f"Progresso: {progresso:.1f}%", font=("Arial", 12)).pack(anchor="w")
            ctk.CTkProgressBar(frame, value=progresso/100).pack(fill="x", padx=4, pady=2)
            ctk.CTkLabel(frame, text=f"Prazo: {prazo or '-'} | Prioridade: {prioridade} | {desc or ''}", font=("Arial", 11, "italic")).pack(anchor="w")

# Formulário de objetivo
class ObjetivoForm(ctk.CTkFrame):
    def __init__(self, master, usuario_id, main_app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_id = usuario_id
        self.main_app = main_app
        self.on_save = main_app.refresh_objetivos
        self.nome_var = ctk.StringVar()
        self.meta_var = ctk.StringVar()
        self.prazo_var = ctk.StringVar()
        self.prioridade_var = ctk.StringVar(value="1")
        self.desc_var = ctk.StringVar()
        ctk.CTkLabel(self, text="Nome do objetivo:").grid(row=0, column=0, padx=2)
        ctk.CTkEntry(self, textvariable=self.nome_var, width=120).grid(row=0, column=1, padx=2)
        ctk.CTkLabel(self, text="Meta (R$):").grid(row=0, column=2, padx=2)
        ctk.CTkEntry(self, textvariable=self.meta_var, width=80).grid(row=0, column=3, padx=2)
        ctk.CTkLabel(self, text="Prazo (AAAA-MM-DD):").grid(row=1, column=0, padx=2)
        ctk.CTkEntry(self, textvariable=self.prazo_var, width=100).grid(row=1, column=1, padx=2)
        ctk.CTkLabel(self, text="Prioridade:").grid(row=1, column=2, padx=2)
        ctk.CTkEntry(self, textvariable=self.prioridade_var, width=40).grid(row=1, column=3, padx=2)
        ctk.CTkLabel(self, text="Descrição:").grid(row=2, column=0, padx=2)
        ctk.CTkEntry(self, textvariable=self.desc_var, width=200).grid(row=2, column=1, columnspan=3, padx=2)
        self.msg = ctk.CTkLabel(self, text="", text_color="red")
        self.msg.grid(row=3, column=0, columnspan=4)
        ctk.CTkButton(self, text="Salvar objetivo", command=self.salvar).grid(row=4, column=0, columnspan=4, pady=4)

    def salvar(self):
        from database import inserir_objetivo
        nome = self.nome_var.get().strip()
        meta = self.meta_var.get().replace(",", ".")
        prazo = self.prazo_var.get().strip()
        prioridade = self.prioridade_var.get().strip()
        desc = self.desc_var.get().strip()
        if not (nome and meta):
            self.msg.configure(text="Preencha nome e meta.")
            return
        try:
            meta = float(meta)
            prioridade = int(prioridade)
        except ValueError:
            self.msg.configure(text="Meta/prioridade inválida.")
            return
        try:
            inserir_objetivo(self.usuario_id, nome, meta, prazo or None, prioridade, desc)
            self.msg.configure(text="Objetivo salvo!", text_color="green")
            self.on_save()
        except Exception as e:
            self.msg.configure(text="Erro: " + str(e), text_color="red")



    def show_lancamentos(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.main_frame, text="Lançamentos (Gastos/Investimentos)", font=("Arial", 18)).pack(pady=10)
        CategoriaForm(self.main_frame, self).pack(pady=4)
        LancamentoForm(self.main_frame, self.usuario_id, self.refresh_lancamentos).pack(pady=10)
        self.lanc_list_frame = ctk.CTkFrame(self.main_frame)
        self.lanc_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_lancamentos()
# Formulário de categoria
class CategoriaForm(ctk.CTkFrame):
    def __init__(self, master, main_app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.main_app = main_app
        self.on_save = main_app.refresh_lancamentos
        self.nome_var = ctk.StringVar()
        self.tipo_var = ctk.StringVar(value="gasto")
        ctk.CTkLabel(self, text="Nova Categoria:").grid(row=0, column=0, padx=2)
        ctk.CTkEntry(self, textvariable=self.nome_var, width=120, placeholder_text="Nome da categoria").grid(row=0, column=1, padx=2)
        ctk.CTkOptionMenu(self, variable=self.tipo_var, values=["gasto", "investimento"]).grid(row=0, column=2, padx=2)
        ctk.CTkButton(self, text="Adicionar", command=self.salvar).grid(row=0, column=3, padx=2)
        self.msg = ctk.CTkLabel(self, text="", text_color="red")
        self.msg.grid(row=1, column=0, columnspan=4)

    def salvar(self):
        from database import inserir_categoria
        nome = self.nome_var.get().strip()
        tipo = self.tipo_var.get()
        if not nome:
            self.msg.configure(text="Informe o nome da categoria.")
            return
        try:
            inserir_categoria(nome, tipo)
            self.msg.configure(text="Categoria adicionada!", text_color="green")
            self.on_save()
        except Exception as e:
            self.msg.configure(text="Erro: " + str(e), text_color="red")

    # Removido: refresh_lancamentos duplicado

# Formulário de lançamento
class LancamentoForm(ctk.CTkFrame):
    def __init__(self, master, usuario_id, on_save, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_id = usuario_id
        self.on_save = on_save
        self.tipo_var = ctk.StringVar(value="gasto")
        self.categoria_var = ctk.StringVar()
        self.valor_var = ctk.StringVar()
        self.data_var = ctk.StringVar()
        self.obs_var = ctk.StringVar()
        ctk.CTkLabel(self, text="Tipo:").grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkOptionMenu(self, variable=self.tipo_var, values=["gasto", "investimento"], command=self.update_categorias).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkLabel(self, text="Categoria:").grid(row=0, column=2, padx=2, pady=2)
        self.categoria_menu = ctk.CTkOptionMenu(self, variable=self.categoria_var, values=[])
        self.categoria_menu.grid(row=0, column=3, padx=2, pady=2)
        ctk.CTkLabel(self, text="Valor:").grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkEntry(self, textvariable=self.valor_var, width=80).grid(row=1, column=1, padx=2, pady=2)
        ctk.CTkLabel(self, text="Data (AAAA-MM-DD):").grid(row=1, column=2, padx=2, pady=2)
        ctk.CTkEntry(self, textvariable=self.data_var, width=100).grid(row=1, column=3, padx=2, pady=2)
        ctk.CTkLabel(self, text="Obs:").grid(row=2, column=0, padx=2, pady=2)
        ctk.CTkEntry(self, textvariable=self.obs_var, width=200).grid(row=2, column=1, columnspan=3, padx=2, pady=2)
        self.msg = ctk.CTkLabel(self, text="", text_color="red")
        self.msg.grid(row=3, column=0, columnspan=4)
        ctk.CTkButton(self, text="Salvar", command=self.salvar).grid(row=4, column=0, columnspan=4, pady=4)
        self.update_categorias()

    def update_categorias(self, *_):
        from database import buscar_categorias
        tipo = self.tipo_var.get()
        cats = buscar_categorias(tipo)
        if not cats:
            self.categoria_menu.configure(values=["Cadastre categorias"], state="disabled")
        else:
            nomes = [c[1] for c in cats]
            self.categoria_menu.configure(values=nomes, state="normal")
            self.categoria_var.set(nomes[0])

    def salvar(self):
        from database import buscar_categorias, inserir_lancamento
        tipo = self.tipo_var.get()
        categoria_nome = self.categoria_var.get()
        valor = self.valor_var.get().replace(",", ".")
        data = self.data_var.get()
        obs = self.obs_var.get()
        if not (tipo and categoria_nome and valor and data):
            self.msg.configure(text="Preencha todos os campos obrigatórios.")
            return
        try:
            valor = float(valor)
        except ValueError:
            self.msg.configure(text="Valor inválido.")
            return
        # Buscar id da categoria
        cats = buscar_categorias(tipo)
        cat_id = None
        for c in cats:
            if c[1] == categoria_nome:
                cat_id = c[0]
                break
        if not cat_id:
            self.msg.configure(text="Categoria inválida.")
            return
        try:
            inserir_lancamento(tipo, cat_id, valor, data, obs, self.usuario_id)
            self.msg.configure(text="Lançamento salvo!", text_color="green")
            self.on_save()
        except Exception as e:
            self.msg.configure(text="Erro: " + str(e), text_color="red")


    def show_relatorios(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.main_frame, text="Relatórios", font=("Arial", 18)).pack(pady=10)
        btn_csv = ctk.CTkButton(self.main_frame, text="Exportar lançamentos para CSV", command=self.exportar_csv)
        btn_csv.pack(pady=8)
        btn_graf = ctk.CTkButton(self.main_frame, text="Gráfico de Gastos por Categoria", command=self.mostrar_grafico_gastos)
        btn_graf.pack(pady=4)
        self.relatorio_list_frame = ctk.CTkFrame(self.main_frame)
        self.relatorio_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_relatorio_list()

    def mostrar_grafico_gastos(self):
        from database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.nome, SUM(l.valor) FROM lancamentos l
            JOIN categorias c ON l.categoria_id = c.id
            WHERE l.usuario_id=%s AND l.tipo='gasto'
            GROUP BY c.nome
        """, (self.usuario_id,))
        dados = cur.fetchall()
        cur.close()
        conn.close()
        if not dados:
            from tkinter import messagebox
            messagebox.showinfo("Gráfico", "Nenhum gasto para exibir.")
            return
        from charts import grafico_gastos
        grafico_gastos(dados)
        cur.close()
        conn.close()
        if not dados:
            messagebox.showinfo("Gráfico", "Nenhum gasto para exibir.")
            return
        from charts import grafico_gastos
        grafico_gastos(dados)
        self.relatorio_list_frame = ctk.CTkFrame(self.main_frame)
        self.relatorio_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_relatorio_list()

    def refresh_relatorio_list(self):
        for widget in self.relatorio_list_frame.winfo_children():
            widget.destroy()
        from database import buscar_lancamentos
        lancs = buscar_lancamentos(self.usuario_id)
        if not lancs:
            ctk.CTkLabel(self.relatorio_list_frame, text="Nenhum lançamento cadastrado.").pack()
            return
        for l in lancs:
            ctk.CTkLabel(self.relatorio_list_frame, text=f"{l[1].capitalize()} | {l[2]} | R$ {l[3]:.2f} | {l[4]} | {l[5] or ''}", anchor="w").pack(fill="x", padx=8, pady=2)

    def exportar_csv(self):
        from database import buscar_lancamentos
        lancs = buscar_lancamentos(self.usuario_id)
        if not lancs:
            from tkinter import messagebox
            messagebox.showinfo("Exportar CSV", "Nenhum lançamento para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Salvar relatório CSV")
        if not path:
            return
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipo", "Categoria", "Valor", "Data", "Observação"])
            for l in lancs:
                writer.writerow([l[1], l[2], f"{l[3]:.2f}", l[4], l[5] or ""])
        from tkinter import messagebox
        messagebox.showinfo("Exportar CSV", f"Relatório exportado para {path}")

    def show_configuracoes(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.main_frame, text="Configurações (em breve)", font=("Arial", 18)).pack(pady=10)

    def clear_main(self):
        for widget in self.winfo_children():
            if not isinstance(widget, LoginFrame):
                widget.destroy()

# Menu lateral
class MenuLateral(ctk.CTkFrame):
    def __init__(self, master, callback, *args, **kwargs):
        super().__init__(master, width=180, *args, **kwargs)
        self.callback = callback
        self.configure(fg_color="#222831")
        ctk.CTkLabel(self, text="Menu", font=("Arial", 16, "bold"), text_color="#00adb5").pack(pady=18)
        for nome in ["Dashboard", "Lançamentos", "Objetivos", "Orçamento", "Relatórios", "Configurações", "Sair"]:
            ctk.CTkButton(self, text=nome, command=lambda n=nome: self.callback(n), width=150).pack(pady=6)

    def logout(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.pack(expand=True)

def run_app():
    init_db()
    app = MainApp()
    app.mainloop()
