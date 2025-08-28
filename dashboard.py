
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===============================
# BANCO DE DADOS
# ===============================
def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data TEXT NOT NULL,
            status TEXT DEFAULT 'OK',
            data_pagamento TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE,
            valor TEXT
        )
    """)
    conn.commit()
    conn.close()

# ===============================
# FUNÇÕES AUXILIARES
# ===============================
def calcular_saldo():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM lancamentos WHERE tipo='Receita'")
    receitas = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(valor) FROM lancamentos WHERE tipo='Gasto'")
    despesas = cursor.fetchone()[0] or 0
    saldo = receitas - despesas
    conn.close()
    return receitas, despesas, saldo

def inserir_lancamento(tipo, valor, categoria, data_pagamento=None):
    if not categoria:
        categoria = "Outros"
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lancamentos (tipo, valor, categoria, data, data_pagamento)
        VALUES (?, ?, ?, ?, ?)
    """, (
        tipo, valor, categoria, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data_pagamento
    ))
    conn.commit()
    conn.close()

def listar_ultimos_lancamentos(limit=10):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo, valor, categoria, data, data_pagamento FROM lancamentos
        ORDER BY data DESC, id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Função para remover lançamento
def remover_lancamento(lancamento_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lancamentos WHERE id = ?", (lancamento_id,))
    conn.commit()
    conn.close()

# Função para editar lançamento
def editar_lancamento(lancamento_id, tipo, valor, categoria, data_pagamento=None):
    if not categoria:
        categoria = "Outros"
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lancamentos SET tipo=?, valor=?, categoria=?, data_pagamento=? WHERE id=?
    """, (tipo, valor, categoria, data_pagamento, lancamento_id))
    conn.commit()
    conn.close()

# ===============================
# INTERFACE GRÁFICA
# ===============================
class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Financeiro")
        self.root.geometry("900x650")

        # Frame superior: saldo
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill="x", pady=10)

        self.lbl_receitas = tk.Label(self.frame_top, text="Receitas: R$ 0.00", font=("Arial", 12))
        self.lbl_receitas.pack(side="left", padx=20)

        self.lbl_despesas = tk.Label(self.frame_top, text="Despesas: R$ 0.00", font=("Arial", 12))
        self.lbl_despesas.pack(side="left", padx=20)

        self.lbl_saldo = tk.Label(self.frame_top, text="Saldo: R$ 0.00", font=("Arial", 14, "bold"))
        self.lbl_saldo.pack(side="left", padx=20)

        self.btn_novo = tk.Button(self.frame_top, text="Novo Lançamento", command=self.abrir_janela_lancamento)
        self.btn_novo.pack(side="right", padx=20)

        # Frame central: gráfico e lista
        self.frame_center = tk.Frame(root)
        self.frame_center.pack(fill="both", expand=True)

        self.frame_graph = tk.Frame(self.frame_center)
        self.frame_graph.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.frame_list = tk.Frame(self.frame_center)
        self.frame_list.pack(side="right", fill="y", padx=10, pady=10)

        self.atualizar_dashboard()


    def atualizar_dashboard(self):
        # Atualiza saldo, receitas e despesas
        receitas, despesas, saldo = calcular_saldo()
        self.lbl_receitas.config(text=f"Receitas: R$ {receitas:.2f}")
        self.lbl_despesas.config(text=f"Despesas: R$ {despesas:.2f}")
        self.lbl_saldo.config(text=f"Saldo: R$ {saldo:.2f}")

        # Limpa widgets antigos do frame_list e frame_graph
        for widget in self.frame_list.winfo_children():
            widget.destroy()
        for widget in self.frame_graph.winfo_children():
            widget.destroy()

        # Lista de lançamentos recentes
        tk.Label(self.frame_list, text="Últimos Lançamentos", font=("Arial", 12, "bold")).pack(pady=5)
        self.tree = ttk.Treeview(self.frame_list, columns=("id", "tipo", "valor", "categoria", "data"), show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("data", text="Data")
        self.tree.column("id", width=30)
        self.tree.column("tipo", width=70)
        self.tree.column("valor", width=70)
        self.tree.column("categoria", width=100)
        self.tree.column("data", width=120)
        for row in listar_ultimos_lancamentos(10):
            id_, tipo, valor, categoria, data, _ = row
            categoria = categoria if categoria else "Outros"
            self.tree.insert("", "end", values=(id_, tipo, f"R$ {valor:.2f}", categoria, data[:16]))
        self.tree.pack(pady=5)

        # Botões de editar e remover
        btn_frame = tk.Frame(self.frame_list)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Editar", command=self.abrir_janela_editar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remover", command=self.remover_lancamento_selecionado).pack(side="left", padx=5)

        # Gráfico de pizza das categorias de gastos
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT categoria, SUM(valor) FROM lancamentos WHERE tipo='Gasto' GROUP BY categoria")
        dados = cursor.fetchall()
        conn.close()
        categorias = [d[0] if d[0] else 'Outros' for d in dados]
        valores = [d[1] for d in dados]
        if valores:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=90)
            ax.set_title('Gastos por Categoria')
            canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            tk.Label(self.frame_graph, text="Sem dados para exibir o gráfico.", font=("Arial", 12)).pack(pady=20)

    def remover_lancamento_selecionado(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um lançamento para remover.")
            return
        valores = self.tree.item(item[0], "values")
        lancamento_id = valores[0]
        if messagebox.askyesno("Remover", "Tem certeza que deseja remover este lançamento?"):
            remover_lancamento(lancamento_id)
            self.atualizar_dashboard()

    def abrir_janela_editar(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um lançamento para editar.")
            return
        valores = self.tree.item(item[0], "values")
        lancamento_id, tipo, valor, categoria, data = valores
        valor = valor.replace("R$ ", "").replace(",", ".")

        janela = tk.Toplevel(self.root)
        janela.title("Editar Lançamento")
        janela.geometry("340x340")

        tk.Label(janela, text="Tipo:").pack(pady=5)
        tipo_cb = ttk.Combobox(janela, values=["Receita", "Gasto", "Conta a Pagar"])
        tipo_cb.set(tipo)
        tipo_cb.pack(pady=5)
        tk.Label(janela, text="Valor:").pack(pady=5)
        valor_entry = tk.Entry(janela)
        valor_entry.insert(0, valor)
        valor_entry.pack(pady=5)
        tk.Label(janela, text="Categoria:").pack(pady=5)
        categoria_entry = tk.Entry(janela)
        categoria_entry.insert(0, categoria)
        categoria_entry.pack(pady=5)
        tk.Label(janela, text="Data de Pagamento (apenas para Conta a Pagar) [AAAA-MM-DD]:").pack(pady=5)
        data_pgto_entry = tk.Entry(janela)
        data_pgto_entry.pack(pady=5)

        def salvar_edicao():
            try:
                novo_valor = float(valor_entry.get())
                novo_tipo = tipo_cb.get()
                nova_categoria = categoria_entry.get() or None
                novo_data_pgto = data_pgto_entry.get().strip() or None
                if novo_tipo not in ["Receita", "Gasto", "Conta a Pagar"]:
                    raise ValueError("Selecione um tipo válido")
                if novo_tipo == "Conta a Pagar":
                    if not novo_data_pgto:
                        raise ValueError("Informe a data de pagamento para Conta a Pagar")
                    editar_lancamento(lancamento_id, "Gasto", novo_valor, nova_categoria, novo_data_pgto)
                else:
                    editar_lancamento(lancamento_id, novo_tipo, novo_valor, nova_categoria, None)
                messagebox.showinfo("Sucesso", "Lançamento editado!")
                janela.destroy()
                self.atualizar_dashboard()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Salvar", command=salvar_edicao).pack(pady=10)

        # Gráfico de pizza das categorias de gastos
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT categoria, SUM(valor) FROM lancamentos WHERE tipo='Gasto' GROUP BY categoria")
        dados = cursor.fetchall()
        conn.close()
        categorias = [d[0] if d[0] else 'Outros' for d in dados]
        valores = [d[1] for d in dados]
        if valores:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=90)
            ax.set_title('Gastos por Categoria')
            canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            tk.Label(self.frame_graph, text="Sem dados para exibir o gráfico.", font=("Arial", 12)).pack(pady=20)

    # ...existing code...

    def abrir_janela_lancamento(self):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Lançamento ou Conta a Pagar")
        janela.geometry("340x340")

        tk.Label(janela, text="Tipo:").pack(pady=5)
        tipo_cb = ttk.Combobox(janela, values=["Receita", "Gasto", "Conta a Pagar"])
        tipo_cb.pack(pady=5)
        tk.Label(janela, text="Valor:").pack(pady=5)
        valor_entry = tk.Entry(janela)
        valor_entry.pack(pady=5)
        tk.Label(janela, text="Categoria:").pack(pady=5)
        categoria_entry = tk.Entry(janela)
        categoria_entry.pack(pady=5)
        tk.Label(janela, text="Data de Pagamento (apenas para Conta a Pagar) [AAAA-MM-DD]:").pack(pady=5)
        data_pgto_entry = tk.Entry(janela)
        data_pgto_entry.pack(pady=5)

        def salvar():
            try:
                valor = float(valor_entry.get())
                tipo = tipo_cb.get()
                categoria = categoria_entry.get() or None
                data_pgto = data_pgto_entry.get().strip() or None
                if tipo not in ["Receita", "Gasto", "Conta a Pagar"]:
                    raise ValueError("Selecione um tipo válido")
                if tipo == "Conta a Pagar":
                    if not data_pgto:
                        raise ValueError("Informe a data de pagamento para Conta a Pagar")
                    inserir_lancamento("Gasto", valor, categoria, data_pgto)
                else:
                    inserir_lancamento(tipo, valor, categoria, None)
                messagebox.showinfo("Sucesso", "Lançamento adicionado!")
                janela.destroy()
                self.atualizar_dashboard()
            except Exception as e:
                messagebox.showerror("Erro", str(e))


        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)

# Bloco principal ao final do arquivo
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
input("Pressione Enter para sair...")
