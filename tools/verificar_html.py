#!/usr/bin/env python3
"""Validacao basica do HTML e JavaScript do Jorge (sem dependencias externas).

Este teste verifica estrutura da pagina, botoes e sintaxe do script.
Nao substitui um teste visual no navegador ou no celular.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile


class Leitor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.canvas = []

    def handle_starttag(self, tag, attrs):
        dados = dict(attrs)
        if "id" in dados:
            self.ids.add(dados["id"])
        if tag == "canvas":
            self.canvas.append(dados)


def verificar(arquivo: Path) -> None:
    html = arquivo.read_text(encoding="utf-8")
    leitor = Leitor()
    leitor.feed(html)

    obrigatorios = {
        "jogo", "area", "hud", "menu", "iniciar",
        "vidas", "pontos", "acelerar", "frear", "subir",
        "descer", "telaCheia",
    }
    ausentes = sorted(obrigatorios - leitor.ids)
    if ausentes:
        raise RuntimeError("Elementos ausentes: " + ", ".join(ausentes))

    if len(leitor.canvas) != 1:
        raise RuntimeError("Esperado exatamente um canvas principal")
    tela = leitor.canvas[0]
    if tela.get("width") != "900" or tela.get("height") != "500":
        raise RuntimeError("Resolucao interna mudou; revisar logica do jogo")

    scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", html, flags=re.I | re.S)
    if len(scripts) != 1:
        raise RuntimeError("Esperado um bloco JavaScript dentro do HTML")
    codigo = scripts[0]

    for trecho in ("requestAnimationFrame(loop)", "function iniciar()", "function mudarFaixa(",
                   "requestFullscreen", "fullscreenchange"):
        if trecho not in codigo:
            raise RuntimeError("Funcao esperada ausente: " + trecho)

    if "image-rendering:pixelated" in html and "drawImage(pixels" not in codigo:
        raise RuntimeError("Pixel Art: renderizacao em baixa resolucao ausente")

    with tempfile.TemporaryDirectory() as pasta:
        js = Path(pasta) / "jogo.js"
        js.write_text(codigo, encoding="utf-8")
        subprocess.run(["node", "--check", str(js)], check=True)

    print(f"OK: {arquivo} - elementos, canvas e sintaxe JavaScript validados")
    print("Observacao: aparencia e controles reais devem ser testados no dispositivo.")


if __name__ == "__main__":
    verificar(Path(sys.argv[1] if len(sys.argv) > 1 else "index.html"))
