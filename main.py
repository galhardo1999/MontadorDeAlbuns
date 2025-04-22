import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class AlbumMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Montador de Álbuns de Formatura")

        # Definir tamanho inicial da janela como 80% da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.root.geometry(f"{window_width}x{window_height}")

        self.fotos_selecionadas = []
        self.album_paginas = []
        self.modelos_paginas = []
        self.pagina_atual = 0
        self.fundo_atual = "white"
        self.fundo_imagem = None
        self.imagens_fundo = []
        self.fotos_selecionadas_miniaturas = []

        self.diretorio_selecionado = r"C:\Montar Albuns"
        if not os.path.exists(self.diretorio_selecionado):
            os.makedirs(self.diretorio_selecionado)

        self.configurar_interface()

        self.icone_pasta = self.criar_icone_pasta()
        self.icone_imagem = self.criar_icone_imagem()

        self.carregar_diretorio()

        # Vincular evento de redimensionamento
        self.canvas.bind("<Configure>", self.on_resize)

    def configurar_interface(self):
        self.frame_botoes = ttk.Frame(self.root)
        self.frame_botoes.pack(fill="x", padx=10, pady=5)

        ttk.Button(self.frame_botoes, text="Adicionar Foto", command=self.adicionar_ao_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Organizar Álbum", command=self.organizar_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Limpar Álbum", command=self.limpar_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Salvar Álbum", command=self.salvar_album).pack(side="right", padx=5)

        # Criar canvas principal com barra de rolagem
        self.canvas_principal = tk.Canvas(self.root)
        self.scrollbar_y = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas_principal.yview)
        self.canvas_principal.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame principal dentro do canvas
        self.frame_principal = ttk.Frame(self.canvas_principal)
        self.canvas_principal.create_window((0, 0), window=self.frame_principal, anchor="nw")

        self.frame_esquerda = ttk.Frame(self.frame_principal)
        self.frame_esquerda.pack(side="left", fill="y", padx=5)

        ttk.Label(self.frame_esquerda, text="Explorador de Arquivos").pack()
        self.arvore = ttk.Treeview(self.frame_esquerda, show="tree", height=10, selectmode="extended")
        self.arvore.pack(fill="x", pady=5)
        self.arvore.bind("<<TreeviewSelect>>", self.selecionar_item_arvore)

        ttk.Label(self.frame_esquerda, text="Pré-visualização").pack()
        self.canvas_prev = tk.Canvas(self.frame_esquerda, bg="white", width=150, height=150)
        self.canvas_prev.pack(pady=5)

        self.frame_canvas = ttk.Frame(self.frame_principal)
        self.frame_canvas.pack(side="left", fill="both", expand=True, padx=5)

        # Aumentar o tamanho inicial do canvas
        self.canvas = tk.Canvas(self.frame_canvas, bg="white", width=700, height=500)  # Increased size
        self.canvas.pack(fill="both", expand=True, pady=10)

        self.label_pagina = ttk.Label(self.frame_canvas, text="Nenhum álbum criado")
        self.label_pagina.pack()

        self.frame_navegacao = ttk.Frame(self.frame_canvas)
        self.frame_navegacao.pack(pady=5)

        self.botao_anterior = ttk.Button(self.frame_navegacao, text="Página Anterior", command=self.pagina_anterior, state="disabled")
        self.botao_anterior.pack(side="left", padx=5)
        self.botao_proxima = ttk.Button(self.frame_navegacao, text="Próxima Página", command=self.proxima_pagina, state="disabled")
        self.botao_proxima.pack(side="left", padx=5)

        # Frame da direita com padding mínimo à direita
        self.frame_direita = ttk.Frame(self.frame_principal)
        self.frame_direita.pack(side="right", fill="y", padx=(5, 0))  # Reduced right padding

        ttk.Label(self.frame_direita, text="Modelos").pack()
        self.modelos = [
            ("Modelo 1: 1 foto", 1),
            ("Modelo 2: 2 fotos", 2),
            ("Modelo 3: 3 fotos", 3),
            ("Modelo 4: 4 fotos", 4)
        ]
        for texto, num_fotos in self.modelos:
            ttk.Button(self.frame_direita, text=texto, command=lambda n=num_fotos: self.selecionar_modelo(n)).pack(fill="x", pady=2)

        # Adicionar seção de Fundos ao frame_direita
        ttk.Label(self.frame_direita, text="Fundos").pack(pady=5)
        self.frame_fundos = ttk.Frame(self.frame_direita)
        self.frame_fundos.pack(pady=5)

        ttk.Button(self.frame_fundos, text="Selecionar Pasta de Fundos", command=self.carregar_fundos).pack(pady=5)

        self.canvas_fundos = tk.Canvas(self.frame_fundos, bg="white", width=150, height=80)
        self.canvas_fundos.pack(pady=5)
        self.canvas_fundos.bind("<Button-1>", self.selecionar_fundo)

        # Frame de miniaturas na parte inferior e centralizado
        self.frame_miniaturas = ttk.Frame(self.root)
        self.frame_miniaturas.pack(side="bottom", fill="x", padx=10, pady=5)

        self.frame_miniaturas_inner = ttk.Frame(self.frame_miniaturas)
        self.frame_miniaturas_inner.pack(expand=True)

        ttk.Label(self.frame_miniaturas_inner, text="Minhas Fotos").pack(side="left")
        self.canvas_miniaturas = tk.Canvas(self.frame_miniaturas_inner, bg="white", height=80, width=750)
        self.canvas_miniaturas.pack(side="left", padx=5)
        self.canvas_miniaturas.bind("<Button-1>", self.selecionar_miniatura)

        ttk.Button(self.frame_miniaturas_inner, text="Deletar Fotos", command=self.deletar_fotos_selecionadas).pack(side="left", padx=5)
        ttk.Button(self.frame_miniaturas_inner, text="Ordenar Páginas", command=self.ordenar_paginas).pack(side="right", padx=5)

        # Atualizar região de rolagem
        self.frame_principal.bind("<Configure>", lambda e: self.canvas_principal.configure(scrollregion=self.canvas_principal.bbox("all")))

    def on_resize(self, event):
        self.atualizar_previsualizacao()

    def criar_icone_pasta(self):
        img = Image.new("RGB", (16, 16), "yellow")
        return ImageTk.PhotoImage(img)

    def criar_icone_imagem(self):
        img = Image.new("RGB", (16, 16), "red")
        return ImageTk.PhotoImage(img)

    def carregar_diretorio(self):
        diretorio = self.diretorio_selecionado
        for item in self.arvore.get_children():
            self.arvore.delete(item)
        raiz_id = self.arvore.insert("", "end", text=os.path.basename(diretorio), open=True, image=self.icone_pasta)
        self.carregar_subdiretorios(diretorio, raiz_id)

    def carregar_subdiretorios(self, diretorio, pai):
        for item in sorted(os.listdir(diretorio)):
            caminho = os.path.join(diretorio, item)
            if os.path.isdir(caminho):
                item_id = self.arvore.insert(pai, "end", text=item, image=self.icone_pasta)
                self.carregar_subdiretorios(caminho, item_id)
            elif item.lower().endswith((".png", ".jpg", ".jpeg")):
                self.arvore.insert(pai, "end", text=item, image=self.icone_imagem, values=(caminho,))

    def carregar_fundos(self):
        diretorio = filedialog.askdirectory()
        if not diretorio:
            return
        self.imagens_fundo = []
        for item in os.listdir(diretorio):
            caminho = os.path.join(diretorio, item)
            if os.path.isfile(caminho) and item.lower().endswith((".png", ".jpg", ".jpeg")):
                self.imagens_fundo.append(caminho)
        self.canvas_fundos.delete("all")
        self.canvas_fundos.fundos = []
        x_offset = 10
        for caminho in self.imagens_fundo:
            img = Image.open(caminho)
            img.thumbnail((60, 60))
            fundo = ImageTk.PhotoImage(img)
            self.canvas_fundos.create_image(x_offset + 30, 40, image=fundo)
            self.canvas_fundos.fundos.append(fundo)
            x_offset += 70

    def selecionar_fundo(self, event):
        x = event.x
        idx = x // 70
        if idx < len(self.imagens_fundo):
            self.fundo_imagem = self.imagens_fundo[idx]
            self.fundo_atual = None
            self.atualizar_previsualizacao()

    def selecionar_item_arvore(self, event):
        selecionados = self.arvore.selection()
        if not selecionados:
            self.canvas_prev.delete("all")
            return
        item = self.arvore.item(selecionados[-1])
        caminho = item.get("values", [""])[0]
        self.canvas_prev.delete("all")
        if caminho and os.path.isfile(caminho):
            img = Image.open(caminho)
            img.thumbnail((150, 150))
            self.foto_prev = ImageTk.PhotoImage(img)
            self.canvas_prev.create_image(75, 75, image=self.foto_prev)
        else:
            self.canvas_prev.delete("all")

    def adicionar_ao_album(self):
        selecionados = self.arvore.selection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma foto!")
            return
        novas_fotos = 0
        for item_id in selecionados:
            item = self.arvore.item(item_id)
            caminho = item.get("values", [""])[0]
            if caminho and caminho not in self.fotos_selecionadas:
                self.fotos_selecionadas.append(caminho)
                novas_fotos += 1
        if novas_fotos == 0:
            messagebox.showinfo("Aviso", "Nenhuma nova foto foi adicionada (fotos já estão no álbum).")
            return
        self.atualizar_miniaturas()
        self.atualizar_previsualizacao()

    def selecionar_miniatura(self, event):
        x = event.x
        idx = x // 70
        if idx >= len(self.fotos_selecionadas):
            return
        ctrl = (event.state & 0x4) != 0
        shift = (event.state & 0x1) != 0
        if ctrl:
            if idx in self.fotos_selecionadas_miniaturas:
                self.fotos_selecionadas_miniaturas.remove(idx)
            else:
                self.fotos_selecionadas_miniaturas.append(idx)
        elif shift and self.fotos_selecionadas_miniaturas:
            ultimo_idx = self.fotos_selecionadas_miniaturas[-1]
            start = min(ultimo_idx, idx)
            end = max(ultimo_idx, idx)
            self.fotos_selecionadas_miniaturas = list(range(start, end + 1))
        else:
            self.fotos_selecionadas_miniaturas = [idx]
        self.atualizar_miniaturas()

    def deletar_fotos_selecionadas(self):
        if not self.fotos_selecionadas_miniaturas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma foto em 'Minhas Fotos' para deletar!")
            return
        fotos_a_remover = [self.fotos_selecionadas[idx] for idx in sorted(self.fotos_selecionadas_miniaturas, reverse=True)]
        for foto in fotos_a_remover:
            self.fotos_selecionadas.remove(foto)
        self.fotos_selecionadas_miniaturas = []
        self.atualizar_miniaturas()
        self.organizar_album()
        messagebox.showinfo("Sucesso", f"{len(fotos_a_remover)} foto(s) removida(s) do álbum!")

    def selecionar_modelo(self, num_fotos):
        if not self.album_paginas:
            messagebox.showwarning("Aviso", "Organize o álbum primeiro!")
            return
        self.modelos_paginas[self.pagina_atual] = num_fotos
        fotos_anteriores = []
        for i in range(self.pagina_atual):
            fotos_anteriores.extend(self.album_paginas[i])
        fotos_restantes = []
        for i in range(self.pagina_atual, len(self.album_paginas)):
            fotos_restantes.extend(self.album_paginas[i])
        pagina_atual_fotos = fotos_restantes[:num_fotos]
        fotos_sobrando = fotos_restantes[num_fotos:]
        self.album_paginas[self.pagina_atual] = pagina_atual_fotos
        novas_paginas = [pagina_atual_fotos]
        idx = 0
        for i in range(self.pagina_atual + 1, len(self.modelos_paginas)):
            modelo = self.modelos_paginas[i]
            pagina = fotos_sobrando[idx:idx + modelo]
            novas_paginas.append(pagina)
            idx += modelo
        while idx < len(fotos_sobrando):
            modelo = self.modelos_paginas[-1] if self.modelos_paginas else 4
            pagina = fotos_sobrando[idx:idx + modelo]
            novas_paginas.append(pagina)
            self.modelos_paginas.append(modelo)
            idx += modelo
        self.album_paginas = [self.album_paginas[i] for i in range(self.pagina_atual)] + novas_paginas
        while len(self.modelos_paginas) > len(self.album_paginas):
            self.modelos_paginas.pop()
        self.atualizar_previsualizacao()

    def organizar_album(self):
        if not self.fotos_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma foto selecionada!")
            return
        self.album_paginas = []
        self.modelos_paginas = []
        fotos_restantes = self.fotos_selecionadas.copy()
        idx = 0
        while idx < len(fotos_restantes):
            modelo = 4
            pagina = fotos_restantes[idx:idx + modelo]
            self.album_paginas.append(pagina)
            self.modelos_paginas.append(modelo)
            idx += modelo
        self.pagina_atual = 0
        self.botao_anterior.config(state="normal" if self.pagina_atual > 0 else "disabled")
        self.botao_proxima.config(state="normal" if len(self.album_paginas) > 1 else "disabled")
        self.atualizar_previsualizacao()

    def limpar_album(self):
        self.fotos_selecionadas = []
        self.album_paginas = []
        self.modelos_paginas = []
        self.pagina_atual = 0
        self.fotos_selecionadas_miniaturas = []
        self.canvas.delete("all")
        self.canvas_miniaturas.delete("all")
        self.label_pagina.config(text="Nenhum álbum criado")
        self.botao_anterior.config(state="disabled")
        self.botao_proxima.config(state="disabled")
        messagebox.showinfo("Sucesso", "Álbum limpo!")

    def atualizar_previsualizacao(self):
        self.canvas.delete("all")
        if not self.album_paginas or self.pagina_atual >= len(self.album_paginas):
            self.label_pagina.config(text="Nenhum álbum criado")
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 200 or canvas_height < 200:  # Increased minimum size check
            return

        if self.fundo_imagem:
            img_fundo = Image.open(self.fundo_imagem)
            img_fundo = img_fundo.resize((canvas_width, canvas_height), Image.LANCZOS)
            self.fundo_tk = ImageTk.PhotoImage(img_fundo)
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.fundo_tk)
        else:
            self.canvas.configure(bg=self.fundo_atual)

        pagina = self.album_paginas[self.pagina_atual]
        modelo = self.modelos_paginas[self.pagina_atual]
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {len(self.album_paginas)}")

        self.canvas.fotos = []
        max_photo_size = min(canvas_width, canvas_height) * 3 // 4  # Increased photo size
        for i, caminho in enumerate(pagina):
            img = Image.open(caminho)
            if modelo == 1:
                img.thumbnail((max_photo_size, max_photo_size))
            else:
                img.thumbnail((max_photo_size // 2, max_photo_size // 2))
            foto = ImageTk.PhotoImage(img)

            if modelo == 1:
                x, y = canvas_width // 2, canvas_height // 2
            elif modelo == 2:
                x = canvas_width // 4 if i == 0 else 3 * canvas_width // 4
                y = canvas_height // 2
            elif modelo == 3:
                if i == 0:
                    x, y = canvas_width // 2, canvas_height // 4
                else:
                    x = canvas_width // 4 if i == 1 else 3 * canvas_width // 4
                    y = 3 * canvas_height // 4
            else:
                x = canvas_width // 4 if i % 2 == 0 else 3 * canvas_width // 4
                y = canvas_height // 4 if i < 2 else 3 * canvas_height // 4

            self.canvas.create_image(x, y, image=foto)
            self.canvas.fotos.append(foto)

        self.botao_anterior.config(state="normal" if self.pagina_atual > 0 else "disabled")
        self.botao_proxima.config(state="normal" if self.pagina_atual < len(self.album_paginas) - 1 else "disabled")

    def atualizar_miniaturas(self):
        self.canvas_miniaturas.delete("all")
        self.canvas_miniaturas.fotos = []
        x_offset = 10
        for idx, caminho in enumerate(self.fotos_selecionadas):
            img = Image.open(caminho)
            img.thumbnail((60, 60))
            foto = ImageTk.PhotoImage(img)
            self.canvas_miniaturas.create_image(x_offset + 30, 40, image=foto)
            if idx in self.fotos_selecionadas_miniaturas:
                self.canvas_miniaturas.create_rectangle(
                    x_offset, 10, x_offset + 60, 70,
                    outline="red", width=2
                )
            self.canvas_miniaturas.fotos.append(foto)
            x_offset += 70

    def salvar_album(self):
        if not self.album_paginas:
            messagebox.showwarning("Aviso", "Nenhum álbum organizado!")
            return

        pasta_album = os.path.join(self.diretorio_selecionado, "Album")
        if not os.path.exists(pasta_album):
            os.makedirs(pasta_album)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width / canvas_height > 16 / 9:
            output_width = int(canvas_height * 16 / 9)
            output_height = canvas_height
        else:
            output_width = canvas_width
            output_height = int(canvas_width * 9 / 16)

        for idx, pagina in enumerate(self.album_paginas):
            imagem_pagina = Image.new("RGB", (output_width, output_height), self.fundo_atual if not self.fundo_imagem else (255, 255, 255))

            if self.fundo_imagem:
                img_fundo = Image.open(self.fundo_imagem)
                img_fundo = img_fundo.resize((output_width, output_height), Image.LANCZOS)
                imagem_pagina.paste(img_fundo, (0, 0))

            modelo = self.modelos_paginas[idx]
            max_photo_size = min(output_width, output_height) * 3 // 4  # Match increased size
            for i, caminho in enumerate(pagina):
                img = Image.open(caminho)
                if modelo == 1:
                    img.thumbnail((max_photo_size, max_photo_size))
                else:
                    img.thumbnail((max_photo_size // 2, max_photo_size // 2))

                if modelo == 1:
                    x, y = output_width // 2, output_height // 2
                elif modelo == 2:
                    x = output_width // 4 if i == 0 else 3 * output_width // 4
                    y = output_height // 2
                elif modelo == 3:
                    if i == 0:
                        x, y = output_width // 2, output_height // 4
                    else:
                        x = output_width // 4 if i == 1 else 3 * output_width // 4
                        y = 3 * output_height // 4
                else:
                    x = output_width // 4 if i % 2 == 0 else 3 * output_width // 4
                    y = output_height // 4 if i < 2 else 3 * output_height // 4

                img_x = x - img.size[0] // 2
                img_y = y - img.size[1] // 2
                imagem_pagina.paste(img, (img_x, img_y))

            caminho_salvar = os.path.join(pasta_album, f"pagina_{idx + 1}.jpg")
            imagem_pagina.save(caminho_salvar, "JPEG")

        messagebox.showinfo("Sucesso", f"Álbum salvo em {pasta_album}!")

    def ordenar_paginas(self):
        messagebox.showinfo("Ordenar Páginas", "Funcionalidade de ordenação de páginas ainda não implementada.")

    def pagina_anterior(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.atualizar_previsualizacao()

    def proxima_pagina(self):
        if self.pagina_atual < len(self.album_paginas) - 1:
            self.pagina_atual += 1
            self.atualizar_previsualizacao()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlbumMaker(root)
    root.mainloop()