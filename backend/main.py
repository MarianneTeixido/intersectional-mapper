from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3, json, os
from datetime import datetime

app = FastAPI(title="Intersectional Mapper")

# --- CORS: dominio de GitHub Pages de este repo ---
ALLOWED_ORIGINS = [
    "https://marianneteixido.github.io",   # GitHub Pages (MarianneTeixido/intersectional-mapper)
    "http://localhost:8080",               # para desarrollo local
    "http://127.0.0.1:5500",               # Live Server de VSCode
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

DB_PATH = os.environ.get("DB_PATH", "intersectional_mapper.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            creado_en   TEXT NOT NULL,
            actualizado TEXT NOT NULL,
            -- Identificación
            nombre      TEXT,
            contacto    TEXT,
            -- Eje 1: étnico-racial
            raza        TEXT,   -- JSON array
            -- Eje 2: género
            genero      TEXT,   -- JSON array
            genero_otro TEXT,
            expresion   TEXT,   -- JSON array
            -- Eje 3: geopolítica
            lugar_origen    TEXT,
            residencia      TEXT,
            -- Eje 4: clase
            clase           TEXT,
            -- Eje 5: sexualidad
            sexualidad      TEXT,   -- JSON array
            sexualidad_otro TEXT,
            -- Eje 6: sexo asignado
            sexo            TEXT,
            -- Eje 7: migración
            estatus_migratorio TEXT,
            -- Eje 8: discapacidad
            discapacidad    TEXT,   -- JSON array
            discap_otro     TEXT,
            -- Eje 9: edad
            edad            TEXT,
            -- Eje 10: espiritualidad
            espiritualidad  TEXT,   -- JSON array
            espirit_otro    TEXT,
            -- Eje 11: carceral
            situacion_carceral TEXT,
            -- Eje 12: cuerpo
            tamanio_corporal TEXT,
            -- Formación
            nivel_educativo TEXT,
            formacion_no_academica TEXT,  -- JSON array
            noacad_otro     TEXT,
            ocupacion       TEXT,
            -- Posición epistémica
            ep_lugar        TEXT,
            ep_saber        TEXT,
            ep_falta        TEXT,
            ep_tension      TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


class PersonaIn(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    raza: Optional[list] = []
    genero: Optional[list] = []
    genero_otro: Optional[str] = None
    expresion: Optional[list] = []
    lugar_origen: Optional[str] = None
    residencia: Optional[str] = None
    clase: Optional[str] = None
    sexualidad: Optional[list] = []
    sexualidad_otro: Optional[str] = None
    sexo: Optional[str] = None
    estatus_migratorio: Optional[str] = None
    discapacidad: Optional[list] = []
    discap_otro: Optional[str] = None
    edad: Optional[str] = None
    espiritualidad: Optional[list] = []
    espirit_otro: Optional[str] = None
    situacion_carceral: Optional[str] = None
    tamanio_corporal: Optional[str] = None
    nivel_educativo: Optional[str] = None
    formacion_no_academica: Optional[list] = []
    noacad_otro: Optional[str] = None
    ocupacion: Optional[str] = None
    ep_lugar: Optional[str] = None
    ep_saber: Optional[str] = None
    ep_falta: Optional[str] = None
    ep_tension: Optional[str] = None


def row_to_dict(row):
    d = dict(row)
    for field in ["raza", "genero", "expresion", "sexualidad",
                  "discapacidad", "espiritualidad", "formacion_no_academica"]:
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
        else:
            d[field] = []
    return d


@app.get("/")
def root():
    return {"status": "ok", "app": "intersectional-mapper"}


@app.get("/personas")
def listar_personas():
    conn = get_db()
    rows = conn.execute("SELECT * FROM personas ORDER BY creado_en DESC").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.get("/personas/{pid}")
def obtener_persona(pid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return row_to_dict(row)


@app.post("/personas", status_code=201)
def crear_persona(p: PersonaIn):
    ahora = datetime.utcnow().isoformat()
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO personas (
            creado_en, actualizado,
            nombre, contacto,
            raza, genero, genero_otro, expresion,
            lugar_origen, residencia, clase,
            sexualidad, sexualidad_otro, sexo,
            estatus_migratorio,
            discapacidad, discap_otro,
            edad, espiritualidad, espirit_otro,
            situacion_carceral, tamanio_corporal,
            nivel_educativo, formacion_no_academica, noacad_otro,
            ocupacion,
            ep_lugar, ep_saber, ep_falta, ep_tension
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ahora, ahora,
        p.nombre, p.contacto,
        json.dumps(p.raza), json.dumps(p.genero), p.genero_otro, json.dumps(p.expresion),
        p.lugar_origen, p.residencia, p.clase,
        json.dumps(p.sexualidad), p.sexualidad_otro, p.sexo,
        p.estatus_migratorio,
        json.dumps(p.discapacidad), p.discap_otro,
        p.edad, json.dumps(p.espiritualidad), p.espirit_otro,
        p.situacion_carceral, p.tamanio_corporal,
        p.nivel_educativo, json.dumps(p.formacion_no_academica), p.noacad_otro,
        p.ocupacion,
        p.ep_lugar, p.ep_saber, p.ep_falta, p.ep_tension
    ))
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return {"id": nuevo_id, "creado_en": ahora}


@app.put("/personas/{pid}")
def actualizar_persona(pid: int, p: PersonaIn):
    ahora = datetime.utcnow().isoformat()
    conn = get_db()
    exists = conn.execute("SELECT id FROM personas WHERE id=?", (pid,)).fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    conn.execute("""
        UPDATE personas SET
            actualizado=?, nombre=?, contacto=?,
            raza=?, genero=?, genero_otro=?, expresion=?,
            lugar_origen=?, residencia=?, clase=?,
            sexualidad=?, sexualidad_otro=?, sexo=?,
            estatus_migratorio=?,
            discapacidad=?, discap_otro=?,
            edad=?, espiritualidad=?, espirit_otro=?,
            situacion_carceral=?, tamanio_corporal=?,
            nivel_educativo=?, formacion_no_academica=?, noacad_otro=?,
            ocupacion=?,
            ep_lugar=?, ep_saber=?, ep_falta=?, ep_tension=?
        WHERE id=?
    """, (
        ahora, p.nombre, p.contacto,
        json.dumps(p.raza), json.dumps(p.genero), p.genero_otro, json.dumps(p.expresion),
        p.lugar_origen, p.residencia, p.clase,
        json.dumps(p.sexualidad), p.sexualidad_otro, p.sexo,
        p.estatus_migratorio,
        json.dumps(p.discapacidad), p.discap_otro,
        p.edad, json.dumps(p.espiritualidad), p.espirit_otro,
        p.situacion_carceral, p.tamanio_corporal,
        p.nivel_educativo, json.dumps(p.formacion_no_academica), p.noacad_otro,
        p.ocupacion,
        p.ep_lugar, p.ep_saber, p.ep_falta, p.ep_tension,
        pid
    ))
    conn.commit()
    conn.close()
    return {"id": pid, "actualizado": ahora}


@app.delete("/personas/{pid}")
def eliminar_persona(pid: int):
    conn = get_db()
    conn.execute("DELETE FROM personas WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return {"eliminado": pid}


@app.get("/exportar/csv")
def exportar_csv():
    from fastapi.responses import StreamingResponse
    import csv, io
    conn = get_db()
    rows = conn.execute("SELECT * FROM personas ORDER BY creado_en DESC").fetchall()
    conn.close()
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=dict(rows[0]).keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=personas.csv"}
    )
