import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class AlbumMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Montador de Álbuns de Formatura")
        self.root.geometry("1200x700")
        self.root.state('zoomed')  # Maximizar o app ao abrir
        
        # Lista de fotos selecionadas e páginas do álbum
        self.fotos_selecionadas = []
        self.album_paginas = []
        self.modelos_paginas = []  # Lista de modelos para cada página
        self.pagina_atual = 0
        self.fundo_atual = "white"  # Cor de fundo padrão
        self.fundo_imagem = None  # Imagem de fundo (se selecionada)
        self.imagens_fundo = []  # Lista de imagens de fundo
        self.fotos_selecionadas_miniaturas = []  # Lista de índices de miniaturas selecionadas
        
        # Diretório fixo
        self.diretorio_selecionado = r"C:\Montar Albuns"
        if not os.path.exists(self.diretorio_selecionado):
            os.makedirs(self.diretorio_selecionado)
        
        # Configurar interface
        self.configurar_interface()
        
        # Carregar ícones
        self.icone_pasta = self.criar_icone_pasta()
        self.icone_imagem = self.criar_icone_imagem()
        
        # Carregar o diretório fixo automaticamente
        self.carregar_diretorio()

    def configurar_interface(self):
        # Barra superior para botões
        self.frame_botoes = ttk.Frame(self.root)
        self.frame_botoes.pack(fill="x", padx=10, pady=5)
        
        # Botões organizados em grupos
        ttk.Button(self.frame_botoes, text="Adicionar Foto", command=self.adicionar_ao_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Organizar Álbum", command=self.organizar_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Limpar Álbum", command=self.limpar_album).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Salvar Álbum", command=self.salvar_album).pack(side="right", padx=5)
        
        # Frame principal
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame da árvore de diretórios (esquerda)
        self.frame_esquerda = ttk.Frame(self.frame_principal)
        self.frame_esquerda.pack(side="left", fill="y", padx=5)
        
        # Árvore de diretórios com seleção múltipla
        ttk.Label(self.frame_esquerda, text="Explorador de Arquivos").pack()
        self.arvore = ttk.Treeview(self.frame_esquerda, show="tree", height=15, selectmode="extended")
        self.arvore.pack(fill="x", pady=5)
        self.arvore.bind("<<TreeviewSelect>>", self.selecionar_item_arvore)
        
        # Canvas para pré-visualização da foto selecionada
        ttk.Label(self.frame_esquerda, text="Pré-visualização").pack()
        self.canvas_prev = tk.Canvas(self.frame_esquerda, bg="white", width=200, height=200)
        self.canvas_prev.pack(pady=5)
        
        # Seção de fundos
        ttk.Label(self.frame_esquerda, text="Fundos").pack()
        self.frame_fundos = ttk.Frame(self.frame_esquerda)
        self.frame_fundos.pack(pady=5)
        
        # Botão para selecionar pasta de fundos
        ttk.Button(self.frame_fundos, text="Selecionar Pasta de Fundos", command=self.carregar_fundos).pack(pady=5)
        
        # Frame para exibir miniaturas de fundos
        self.canvas_fundos = tk.Canvas(self.frame_fundos, bg="white", width=200, height=100)
        self.canvas_fundos.pack(pady=5)
        self.canvas_fundos.bind("<Button-1>", self.selecionar_fundo)
        
        # Frame do canvas para pré-visualização do álbum (centro)
        self.frame_canvas = ttk.Frame(self.frame_principal)
        self.frame_canvas.pack(side="left", fill="both", expand=True, padx=5)
        
        self.canvas = tk.Canvas(self.frame_canvas, bg="white", width=1280, height=720)
        self.canvas.pack(pady=10)
        
        # Label para informações da página
        self.label_pagina = ttk.Label(self.frame_canvas, text="Nenhum álbum criado")
        self.label_pagina.pack()
        
        # Botões de navegação de páginas
        self.frame_navegacao = ttk.Frame(self.frame_canvas)
        self.frame_navegacao.pack(pady=5)
        
        self.botao_anterior = ttk.Button(self.frame_navegacao, text="Página Anterior", command=self.pagina_anterior, state="disabled")
        self.botao_anterior.pack(side="left", padx=5)
        self.botao_proxima = ttk.Button(self.frame_navegacao, text="Próxima Página", command=self.proxima_pagina, state="disabled")
        self.botao_proxima.pack(side="left", padx=5)
        
        # Frame de modelos (direita)
        self.frame_direita = ttk.Frame(self.frame_principal)
        self.frame_direita.pack(side="right", fill="y", padx=5)
        
        ttk.Label(self.frame_direita, text="Modelos").pack()
        self.modelos = [
            ("Modelo 1: 1 foto", 1),
            ("Modelo 2: 2 fotos", 2),
            ("Modelo 3: 3 fotos", 3),
            ("Modelo 4: 4 fotos", 4)
        ]
        for texto, num_fotos in self.modelos:
            ttk.Button(self.frame_direita, text=texto, command=lambda n=num_fotos: self.selecionar_modelo(n)).pack(fill="x", pady=2)
        
        # Frame inferior para miniaturas
        self.frame_miniaturas = ttk.Frame(self.root)
        self.frame_miniaturas.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(self.frame_miniaturas, text="Minhas Fotos").pack(side="left")
        self.canvas_miniaturas = tk.Canvas(self.frame_miniaturas, bg="white", height=100)
        self.canvas_miniaturas.pack(side="left", fill="x", expand=True, padx=5)
        self.canvas_miniaturas.bind("<Button-1>", self.selecionar_miniatura)
        
        # Botão para deletar fotos selecionadas
        ttk.Button(self.frame_miniaturas, text="Deletar Fotos", command=self.deletar_fotos_selecionadas).pack(side="left", padx=5)
        
        # Botão para ordenar páginas
        ttk.Button(self.frame_miniaturas, text="Ordenar Páginas", command=self.ordenar_paginas).pack(side="right", padx=5)

    def criar_icone_pasta(self):
        # Ícone amarelo para pasta
        img = Image.new("RGB", (16, 16), "yellow")
        return ImageTk.PhotoImage(img)

    def criar_icone_imagem(self):
        # Ícone vermelho para imagem
        img = Image.new("RGB", (16, 16), "red")
        return ImageTk.PhotoImage(img)

    def carregar_diretorio(self):
        # Carregar o diretório fixo C:\Montar Albuns
        diretorio = self.diretorio_selecionado
        
        # Limpar árvore
        for item in self.arvore.get_children():
            self.arvore.delete(item)
        
        # Adicionar diretório raiz
        raiz_id = self.arvore.insert("", "end", text=os.path.basename(diretorio), open=True, image=self.icone_pasta)
        self.carregar_subdiretorios(diretorio, raiz_id)

    def carregar_subdiretorios(self, diretorio, pai):
        # Carregar arquivos e subdiretórios
        for item in sorted(os.listdir(diretorio)):
            caminho = os.path.join(diretorio, item)
            if os.path.isdir(caminho):
                item_id = self.arvore.insert(pai, "end", text=item, image=self.icone_pasta)
                self.carregar_subdiretorios(caminho, item_id)
            elif item.lower().endswith((".png", ".jpg", ".jpeg")):
                self.arvore.insert(pai, "end", text=item, image=self.icone_imagem, values=(caminho,))

    def carregar_fundos(self):
        # Selecionar pasta com imagens de fundo
        diretorio = filedialog.askdirectory()
        if not diretorio:
            return
        
        self.imagens_fundo = []
        for item in os.listdir(diretorio):
            caminho = os.path.join(diretorio, item)
            if os.path.isfile(caminho) and item.lower().endswith((".png", ".jpg", ".jpeg")):
                self.imagens_fundo.append(caminho)
        
        # Atualizar canvas de fundos
        self.canvas_fundos.delete("all")
        self.canvas_fundos.fundos = []
        x_offset = 10
        for caminho in self.imagens_fundo:
            img = Image.open(caminho)
            img.thumbnail((80, 80))
            fundo = ImageTk.PhotoImage(img)
            self.canvas_fundos.create_image(x_offset + 40, 50, image=fundo)
            self.canvas_fundos.fundos.append(fundo)
            x_offset += 90

    def selecionar_fundo(self, event):
        # Selecionar uma imagem de fundo
        x = event.x
        idx = x // 90  # Cada miniatura tem 90 pixels de largura
        if idx < len(self.imagens_fundo):
            self.fundo_imagem = self.imagens_fundo[idx]
            self.fundo_atual = None  # Desativar cor sólida
            self.atualizar_previsualizacao()

    def selecionar_item_arvore(self, event):
        # Exibir pré-visualização da última foto selecionada
        selecionados = self.arvore.selection()
        if not selecionados:
            self.canvas_prev.delete("all")
            return
        
        # Mostrar a última foto selecionada no canvas de pré-visualização
        item = self.arvore.item(selecionados[-1])
        caminho = item.get("values", [""])[0]
        
        self.canvas_prev.delete("all")
        if caminho and os.path.isfile(caminho):
            img = Image.open(caminho)
            img.thumbnail((200, 200))
            self.foto_prev = ImageTk.PhotoImage(img)
            self.canvas_prev.create_image(100, 100, image=self.foto_prev)
        else:
            self.canvas_prev.delete("all")

    def adicionar_ao_album(self):
        # Adicionar todas as fotos selecionadas ao álbum
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
        messagebox.showinfo("Sucesso", f"{novas_fotos} foto(s) adicionada(s) ao álbum!")

    def selecionar_miniatura(self, event):
        # Selecionar múltiplas fotos na seção "Minhas Fotos"
        x = event.x
        idx = x // 90  # Cada miniatura tem 90 pixels de largura
        if idx >= len(self.fotos_selecionadas):
            return
        
        # Verificar se Ctrl ou Shift estão pressionados
        ctrl = (event.state & 0x4) != 0  # Ctrl pressionado
        shift = (event.state & 0x1) != 0  # Shift pressionado
        
        if ctrl:
            # Adicionar ou remover a foto da seleção
            if idx in self.fotos_selecionadas_miniaturas:
                self.fotos_selecionadas_miniaturas.remove(idx)
            else:
                self.fotos_selecionadas_miniaturas.append(idx)
        elif shift and self.fotos_selecionadas_miniaturas:
            # Selecionar intervalo entre a última foto selecionada e a atual
            ultimo_idx = self.fotos_selecionadas_miniaturas[-1]
            start = min(ultimo_idx, idx)
            end = max(ultimo_idx, idx)
            self.fotos_selecionadas_miniaturas = list(range(start, end + 1))
        else:
            # Seleção simples (substitui a seleção anterior)
            self.fotos_selecionadas_miniaturas = [idx]
        
        self.atualizar_miniaturas()

    def deletar_fotos_selecionadas(self):
        # Deletar todas as fotos selecionadas da lista
        if not self.fotos_selecionadas_miniaturas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma foto em 'Minhas Fotos' para deletar!")
            return
        
        # Criar uma lista das fotos a serem removidas
        fotos_a_remover = [self.fotos_selecionadas[idx] for idx in sorted(self.fotos_selecionadas_miniaturas, reverse=True)]
        
        # Remover as fotos da lista
        for foto in fotos_a_remover:
            self.fotos_selecionadas.remove(foto)
        
        # Limpar a seleção
        self.fotos_selecionadas_miniaturas = []
        self.atualizar_miniaturas()
        self.organizar_album()  # Reorganizar o álbum após deletar
        messagebox.showinfo("Sucesso", f"{len(fotos_a_remover)} foto(s) removida(s) do álbum!")

    def selecionar_modelo(self, num_fotos):
        # Aplicar o modelo apenas à página atual
        if not self.album_paginas:
            messagebox.showwarning("Aviso", "Organize o álbum primeiro!")
            return
        
        # Atualizar o modelo da página atual
        self.modelos_paginas[self.pagina_atual] = num_fotos
        
        # Reorganizar a página atual
        fotos_anteriores = []
        for i in range(self.pagina_atual):
            fotos_anteriores.extend(self.album_paginas[i])
        
        fotos_restantes = []
        for i in range(self.pagina_atual, len(self.album_paginas)):
            fotos_restantes.extend(self.album_paginas[i])
        
        # Limitar a página atual ao número de fotos do modelo
        pagina_atual_fotos = fotos_restantes[:num_fotos]
        fotos_sobrando = fotos_restantes[num_fotos:]
        
        # Atualizar a página atual
        self.album_paginas[self.pagina_atual] = pagina_atual_fotos
        
        # Reorganizar as páginas seguintes
        novas_paginas = [pagina_atual_fotos]
        idx = 0
        for i in range(self.pagina_atual + 1, len(self.modelos_paginas)):
            modelo = self.modelos_paginas[i]
            pagina = fotos_sobrando[idx:idx + modelo]
            novas_paginas.append(pagina)
            idx += modelo
        
        # Adicionar novas páginas, se necessário
        while idx < len(fotos_sobrando):
            modelo = self.modelos_paginas[-1] if self.modelos_paginas else 4  # Usar o último modelo ou padrão
            pagina = fotos_sobrando[idx:idx + modelo]
            novas_paginas.append(pagina)
            self.modelos_paginas.append(modelo)
            idx += modelo
        
        # Atualizar album_paginas
        self.album_paginas = [self.album_paginas[i] for i in range(self.pagina_atual)] + novas_paginas
        
        # Ajustar modelos_paginas para corresponder ao número de páginas
        while len(self.modelos_paginas) > len(self.album_paginas):
            self.modelos_paginas.pop()
        
        self.atualizar_previsualizacao()
        messagebox.showinfo("Modelo Selecionado", f"Modelo com {num_fotos} foto(s) aplicado à página {self.pagina_atual + 1}!")

    def organizar_album(self):
        # Organizar fotos em páginas com modelos definidos
        if not self.fotos_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma foto selecionada!")
            return
        
        self.album_paginas = []
        self.modelos_paginas = []
        fotos_restantes = self.fotos_selecionadas.copy()
        idx = 0
        
        # Usar modelo padrão (4) para novas páginas
        while idx < len(fotos_restantes):
            modelo = 4  # Modelo padrão
            pagina = fotos_restantes[idx:idx + modelo]
            self.album_paginas.append(pagina)
            self.modelos_paginas.append(modelo)
            idx += modelo
        
        self.pagina_atual = 0
        self.botao_anterior.config(state="normal" if self.pagina_atual > 0 else "disabled")
        self.botao_proxima.config(state="normal" if len(self.album_paginas) > 1 else "disabled")
        self.atualizar_previsualizacao()
        messagebox.showinfo("Sucesso", f"Álbum organizado com {len(self.album_paginas)} páginas!")

    def limpar_album(self):
        # Limpar álbum e miniaturas
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
        # Atualizar canvas com a página atual do álbum
        self.canvas.delete("all")
        if not self.album_paginas or self.pagina_atual >= len(self.album_paginas):
            self.label_pagina.config(text="Nenhum álbum criado")
            return
        
        # Aplicar fundo (imagem ou cor)
        if self.fundo_imagem:
            img_fundo = Image.open(self.fundo_imagem)
            img_fundo = img_fundo.resize((1280, 720), Image.LANCZOS)
            self.fundo_tk = ImageTk.PhotoImage(img_fundo)
            self.canvas.create_image(640, 360, image=self.fundo_tk)
        else:
            self.canvas.configure(bg=self.fundo_atual)
        
        pagina = self.album_paginas[self.pagina_atual]
        modelo = self.modelos_paginas[self.pagina_atual]
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {len(self.album_paginas)}")
        
        # Exibir fotos com base no modelo da página
        self.canvas.fotos = []  # Armazenar referências
        for i, caminho in enumerate(pagina):
            img = Image.open(caminho)
            # Ajustar tamanho da foto com base no modelo
            if modelo == 1:
                img.thumbnail((600, 600))  # Maior para 1 foto
            else:
                img.thumbnail((300, 300))  # Padrão para 2, 3 ou 4 fotos
            foto = ImageTk.PhotoImage(img)
            
            # Posicionamento das fotos
            if modelo == 1:
                # 1 foto: Centralizada
                x, y = 640, 360
            elif modelo == 2:
                # 2 fotos: Lado a lado
                x = 320 if i == 0 else 960
                y = 360
            elif modelo == 3:
                # 3 fotos: Triângulo (1 topo, 2 baixo)
                if i == 0:
                    x, y = 640, 180
                else:
                    x = 320 if i == 1 else 960
                    y = 540
            else:  # Modelo 4
                # 4 fotos: Grade 2x2
                x = 320 if i % 2 == 0 else 960
                y = 180 if i < 2 else 540
            
            self.canvas.create_image(x, y, image=foto)
            self.canvas.fotos.append(foto)
        
        # Atualizar estado dos botões de navegação
        self.botao_anterior.config(state="normal" if self.pagina_atual > 0 else "disabled")
        self.botao_proxima.config(state="normal" if self.pagina_atual < len(self.album_paginas) - 1 else "disabled")

    def atualizar_miniaturas(self, selecionada=None):
        # Atualizar miniaturas das fotos selecionadas
        self.canvas_miniaturas.delete("all")
        self.canvas_miniaturas.fotos = []
        x_offset = 10
        for idx, caminho in enumerate(self.fotos_selecionadas):
            img = Image.open(caminho)
            img.thumbnail((80, 80))
            foto = ImageTk.PhotoImage(img)
            self.canvas_miniaturas.create_image(x_offset + 40, 50, image=foto)
            if idx in self.fotos_selecionadas_miniaturas:
                self.canvas_miniaturas.create_rectangle(
                    x_offset, 10, x_offset + 80, 90,
                    outline="red", width=2
                )
            self.canvas_miniaturas.fotos.append(foto)
            x_offset += 90

    def salvar_album(self):
        # Salvar cada página do álbum como uma imagem JPEG
        if not self.album_paginas:
            messagebox.showwarning("Aviso", "Nenhum álbum organizado!")
            return
        
        # Criar a pasta "Album" dentro do diretório selecionado
        pasta_album = os.path.join(self.diretorio_selecionado, "Album")
        if not os.path.exists(pasta_album):
            os.makedirs(pasta_album)
        
        # Salvar cada página como JPEG
        for idx, pagina in enumerate(self.album_paginas):
            # Criar uma imagem em branco com o tamanho do canvas (1280x720)
            imagem_pagina = Image.new("RGB", (1280, 720), self.fundo_atual if not self.fundo_imagem else (255, 255, 255))
            
            # Aplicar fundo, se houver
            if self.fundo_imagem:
                img_fundo = Image.open(self.fundo_imagem)
                img_fundo = img_fundo.resize((1280, 720), Image.LANCZOS)
                imagem_pagina.paste(img_fundo, (0, 0))
            
            # Adicionar as fotos à página
            modelo = self.modelos_paginas[idx]
            for i, caminho in enumerate(pagina):
                img = Image.open(caminho)
                # Ajustar tamanho da foto com base no modelo
                if modelo == 1:
                    img.thumbnail((600, 600))
                else:
                    img.thumbnail((300, 300))
                
                # Posicionamento das fotos
                if modelo == 1:
                    x, y = 640, 360
                elif modelo == 2:
                    x = 320 if i == 0 else 960
                    y = 360
                elif modelo == 3:
                    if i == 0:
                        x, y = 640, 180
                    else:
                        x = 320 if i == 1 else 960
                        y = 540
                else:  # Modelo 4
                    x = 320 if i % 2 == 0 else 960
                    y = 180 if i < 2 else 540
                
                # Ajustar a posição para colar a imagem (centralizar no ponto x, y)
                img_x = x - img.size[0] // 2
                img_y = y - img.size[1] // 2
                imagem_pagina.paste(img, (img_x, img_y))
            
            # Salvar a página como JPEG
            caminho_salvar = os.path.join(pasta_album, f"pagina_{idx + 1}.jpg")
            imagem_pagina.save(caminho_salvar, "JPEG")
        
        messagebox.showinfo("Sucesso", f"Álbum salvo em {pasta_album}!")

    def ordenar_paginas(self):
        # Simulação de ordenação de páginas (pode ser expandida)
        messagebox.showinfo("Ordenar Páginas", "Funcionalidade de ordenação de páginas ainda não implementada.")

    def pagina_anterior(self):
        # Navegar para a página anterior
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.atualizar_previsualizacao()

    def proxima_pagina(self):
        # Navegar para a próxima página
        if self.pagina_atual < len(self.album_paginas) - 1:
            self.pagina_atual += 1
            self.atualizar_previsualizacao()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlbumMaker(root)
    root.mainloop()