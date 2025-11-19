Operaciones Soportadas

### SELECT (Read)
```python
gram.produccion_select(["nombre", "edad"], "usuarios", "edad > 18")
# Genera: SELECT nombre, edad FROM usuarios WHERE edad > 18
```

### INSERT (Create)
```python
gram.produccion_insert("usuarios", ["nombre", "edad"], ["Juan", 25])
# Genera: INSERT INTO usuarios (nombre, edad) VALUES ('Juan', 25)
```

### UPDATE (Update)
```python
gram.produccion_update("usuarios", {"edad": 26}, "nombre = 'Juan'")
# Genera: UPDATE usuarios SET edad = 26 WHERE nombre = 'Juan'
```

### DELETE (Delete)
```python
gram.produccion_delete("usuarios", "edad < 18")
# Genera: DELETE FROM usuarios WHERE edad < 18
```



## Producciones Principales
```
S → SELECT | INSERT | UPDATE | DELETE

SELECT → 'SELECT' columnas 'FROM' tabla [condicion]
INSERT → 'INSERT INTO' tabla '(' columnas ')' 'VALUES' '(' valores ')'
UPDATE → 'UPDATE' tabla 'SET' asignaciones [condicion]
DELETE → 'DELETE FROM' tabla [condicion]
```

### Requisitos
- Python 3.9+

### Ejecución
```bash
python SQL_CRUD.py
```

### Ejemplo Básico
```python
from SQL_CRUD import GramaticaSQL, TipoDeDato

# Crear instancia de la gramática
gram = GramaticaSQL()

# Agregar esquema de tabla
gram.ts.agregar_tabla("productos", {
    "id": TipoDeDato.ENTERO,
    "nombre": TipoDeDato.TEXTO,
    "precio": TipoDeDato.REAL,
    "stock": TipoDeDato.ENTERO
})
