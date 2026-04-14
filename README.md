# Shining Soul Remake

Remake de Shining Soul (SEGA/GBA) em Python com Pygame, agora com estrutura modular e gerenciamento moderno de dependencias via `uv`.

## Requisitos

- `uv` instalado
- Linux/Pop!_OS com suporte grafico para abrir janela do Pygame

## Setup rapido

```bash
uv sync
cp .env.example .env
```

## Executar

```bash
uv run python main.py
```

## Comandos de debug em runtime

Esses comandos aparecem no HUD durante a partida:

- V: alterna entre visual Legacy e Voxel
- H: mostra/oculta ajuda de comandos
- TAB: alterna zoom
- T: mostra/oculta profiler
- F1/F2/F3: overlays de grid/chunks/colisao
- F4/F5: HUD de FPS/particulas
- F6/F7: god mode/instant destroy
- F8/F9: burst de particulas/step de regeneracao
- F10/F11/F12: colocar bloco/limpar area/resetar overlay
- 1..5: tipo de bloco
- G/P/C: regen on-off/pausa fisica/limpa particulas

## Testes

```bash
uv run pytest -q
```

## Estrutura

```text
.
├── assets/          # imagens, sprites, audio e dados de mapa
├── core/            # game loop e modulos principais (camera/input/game)
├── entities/        # modelos de entidade e estado
├── utils/           # utilitarios de geometria e assets
├── test/            # testes de sanidade
├── config.py        # configuracao central carregada do .env
├── main.py          # entrypoint
├── pyproject.toml   # dependencias e metadados
└── uv.lock          # lockfile gerado pelo uv
```


