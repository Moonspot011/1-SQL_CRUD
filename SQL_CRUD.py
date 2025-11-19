from typing import Optional
from enum import Enum

class TipoDeDato(Enum):
    ENTERO = "ENTERO"
    TEXTO = "TEXTO"
    BOOLEANO = "BOOLEANO"
    FECHA = "FECHA"
    REAL = "REAL"
    
class OperacionSQL(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
#@dataclass
class Atributo:
    def __init__(self):
        self.tipo: Optional[TipoDeDato] = None
        self.valor: any = None
        self.codigo: str = ""
        self.tabla: str = ""
        self.columnas: list[str] = [] 
        self.valido: bool = True
        self.errores: list[str] = [] 
    
    def __post_init__(self):
            if self.columnas is None:
                self.columnas = []
            if self.errores is None:
                self.errores = []
            
class TablaDeSimbolos:
    def __init__(self):
        self.tablas: dict[str, dict[str, TipoDeDato]] = {}

    def agregar_tabla(self, nombre: str, esquema: dict[str, TipoDeDato]):
        self.tablas[nombre] = esquema
    
    def existe_tabla(self, nombre: str) -> bool:
        return nombre in self.tablas
    
    def existe_columna(self, tabla: str, columna: str) -> bool:
        return tabla in self.tablas and columna in self.tablas[tabla]
    
    def obtener_tipo(self, tabla: str, columna: str) -> Optional[TipoDeDato]:
        if self.existe_columna(tabla, columna):
            return self.tablas[tabla][columna]
        return None
    
class GramaticaSQL:
    def __init__(self):
        self.ts = TablaDeSimbolos()
        self.ts.agregar_tabla("usuarios", {
            "id": TipoDeDato.ENTERO,
            "nombre": TipoDeDato.TEXTO,
            "edad": TipoDeDato.ENTERO,
            "email": TipoDeDato.TEXTO
        })

    def produccion_select(self, columnas: list[str], tabla: str, condicion: Optional[str] = None) -> Atributo:
        atri = Atributo()
    
        # saber si la tabla existe
        
        if not self.ts.existe_tabla(tabla):
            atri.valido = False
            atri.errores.append(f"Tabla '{tabla}' no existe")
            return atri
        
        # verificar que las columnas existan en la tabla
        
        if columnas != ["*"]:
                for col in columnas:
                    if not self.ts.existe_columna(tabla, col):
                        atri.valido = False
                        atri.errores.append(f"Columna '{col}' no existe en '{tabla}'")
                        
        # crear el codigo SQL
        
        columnas_sql = ", ".join(columnas)
        atri.codigo = f"SELECT {columnas_sql} FROM {tabla}"
        if condicion:
            atri.codigo += f" WHERE {condicion}"

        atri.tabla = tabla
        atri.columnas = columnas
        return atri

    # insert
    
    def produccion_insert(self, tabla: str, columnas: list[str],  valores: list[any]) -> Atributo:
        atri = Atributo()
    
        # saber si la tabla existe
        
        if not self.ts.existe_tabla(tabla):
            atri.valido = False
            atri.errores.append(f"Tabla '{tabla}' no existe")
            return atri
        
        # verificar que las columnas existan en la tabla
        
        for col in columnas:
            if not self.ts.existe_columna(tabla, col):
                atri.valido = False
                atri.errores.append(f"Columna '{col}' no existe en '{tabla}'")
        
        # verificar que el numero de columnas y valores coincidan
        
        if len(columnas) != len(valores):
            atri.valido = False
            atri.errores.append("El número de columnas y valores no coincide")
            return atri
        
        # crear el codigo SQL
        
        columnas_sql = ", ".join(columnas)
        valores_sql = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in valores])
        atri.codigo = f"INSERT INTO {tabla} ({columnas_sql}) VALUES ({valores_sql})"
        
        atri.tabla = tabla
        atri.columnas = columnas
        return atri

    #update

    def produccion_update(self, tabla: str, asignaciones: dict[str, any], condicion: Optional[str] = None) -> Atributo:
        atri = Atributo()
        
        # Validar tabla
        if not self.ts.existe_tabla(tabla):
            atri.valido = False
            atri.errores.append(f"Tabla '{tabla}' no existe")
            return atri

        # Validar asignaciones
        set_clauses = []
        for col, val in asignaciones.items():
            if not self.ts.existe_columna(tabla, col):
                atri.valido = False
                atri.errores.append(f"Columna '{col}' no existe en '{tabla}'")
                continue
            
            tipo_esperado = self.ts.obtener_tipo(tabla, col)
            tipo_valor = self._inferir_tipo(val)
            
            if not self._tipos_compatibles(tipo_esperado, tipo_valor):
                atri.valido = False
                atri.errores.append(
                    f"Tipo incompatible para '{col}': "
                    f"esperado {tipo_esperado}, recibido {tipo_valor}"
                )
            
            set_clauses.append(f"{col} = {self._formatear_valor(val)}")
        
        # Generar código
        set_str = ", ".join(set_clauses)
        atri.codigo = f"UPDATE {tabla} SET {set_str}"
        if condicion:
            atri.codigo += f" WHERE {condicion}"

        atri.tabla = tabla
        return atri
    
    def produccion_delete(self, tabla: str, condicion: Optional[str] = None) -> Atributo:
        atri = Atributo()

        # Validar tabla
        if not self.ts.existe_tabla(tabla):
            atri.valido = False
            atri.errores.append(f"Tabla '{tabla}' no existe")
            return atri

        # Generar código
        atri.codigo = f"DELETE FROM {tabla}"
        if condicion:
            atri.codigo += f" WHERE {condicion}"

        atri.tabla = tabla
        return atri
    
    # funciones internas de apoyo
    
    def _inferir_tipo(self, valor: any) -> TipoDeDato:
        if isinstance(valor, int):
            return TipoDeDato.ENTERO
        elif isinstance(valor, float):
            return TipoDeDato.REAL
        elif isinstance(valor, str):
            return TipoDeDato.TEXTO
        elif isinstance(valor, bool):
            return TipoDeDato.BOOLEANO
        return TipoDeDato.TEXTO

    def _tipos_compatibles(self, tipo1: TipoDeDato, tipo2: TipoDeDato) -> bool:
        if tipo1 == tipo2:
            return True
        # ENTERO es compatible con REAL
        if (tipo1 == TipoDeDato.REAL and tipo2 == TipoDeDato.ENTERO):
            return True
        return False
    
    def _formatear_valor(self, valor: any) -> str:
        if isinstance(valor, str):
            return f"'{valor}'"
        elif isinstance(valor, bool):
            return "TRUE" if valor else "FALSE"
        return str(valor)
    
def ejemplos_uso():
    gram = GramaticaSQL()
    
    print("gramatica para SQL-CRUD")
    
    print("\n SELECT:")
    attr = gram.produccion_select(["nombre", "edad"], "usuarios", "edad > 18")
    print(f"   Código: {attr.codigo}")
    print(f"   Válido: {attr.valido}")
    
if __name__ == "__main__":
    ejemplos_uso()
