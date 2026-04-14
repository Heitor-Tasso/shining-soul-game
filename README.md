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


