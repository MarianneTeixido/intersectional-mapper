# Intersectional Mapper

Instrumento de evaluación interseccional para mapear la composición de un grupo
o comunidad a partir de ejes de identidad y posición epistémica. Basado en el
marco teórico de **Crenshaw, Hill Collins, Lugones y Puar**.

El instrumento registra, para cada persona, ejes de primer orden
(origen étnico-racial, género, clase, lugar de origen, sexualidad, educación),
ejes estructurales de segundo orden (estatus migratorio, (des)capacidad, edad,
espiritualidad, situación carceral, corporalidad) y una sección de **posición
epistémica** que recoge saberes situados que los campos cerrados no capturan.

## Arquitectura

- **Frontend** (`docs/`): página estática, sin dependencias, pensada para GitHub Pages.
- **Backend** (`backend/`): API FastAPI con almacenamiento en SQLite, pensada para Render.com.

```
intersectional-mapper/
├── docs/index.html         ← frontend estático (GitHub Pages)
├── backend/                ← API FastAPI + SQLite
│   ├── main.py
│   ├── requirements.txt
│   └── render.yaml
└── README.md
```

> Los datos recogidos son sensibles: la base de datos no se versiona y el
> instrumento debe usarse con consentimiento informado.
