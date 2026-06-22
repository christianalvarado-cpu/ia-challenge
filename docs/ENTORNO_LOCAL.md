# Entorno local

Este proyecto debe ejecutarse con Python 3.11, igual que el proyecto base `multihope`.

## 1. Verificar versiones disponibles

En PowerShell:

```powershell
py -0p
```

Debe aparecer una version `3.11`, por ejemplo:

```text
-V:3.11    C:\Users\chris\AppData\Local\Programs\Python\Python311\python.exe
```

## 2. Crear entorno virtual

Desde la raiz del repositorio:

```powershell
cd C:\Users\chris\Downloads\ia-challenge
py -3.11 -m venv .venv
```

## 3. Activar entorno

```powershell
.\.venv\Scripts\activate
```

## 4. Instalar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Validar entorno

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pytest tests/test_ingest_config.py -q
```

La version esperada es Python 3.11.x.

## 6. Configurar credenciales

Copia la plantilla:

```powershell
Copy-Item .env.example .env
```

Edita `.env` con valores reales:

```text
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

No subas `.env` a GitHub.

## 7. Ejecutar ingesta

```powershell
.\.venv\Scripts\python.exe -m src.run_pipeline
```

## 8. Usar notebook

Abre:

```text
notebooks/00_pipeline_pruebas.ipynb
```

Selecciona el kernel del entorno `.venv` si el editor lo permite.

## 9. Configuracion de Hadoop/winutils en Windows

PySpark en Windows necesita `winutils.exe` para varias operaciones locales de archivos, incluyendo escritura de Parquet. Este proyecto no usa un cluster Hadoop ni HDFS; solo usa `winutils` como compatibilidad local para Spark en Windows.

La configuracion esta centralizada en:

```text
src/utils/spark_session.py
```

Por defecto, el proyecto busca `winutils.exe` en esta ruta, igual que el proyecto base `multihope`:

```text
C:\Users\chris\Downloads\winutils-master\hadoop-3.0.0\bin\winutils.exe
```

En codigo, esa ruta se arma asi:

```python
DEFAULT_WINDOWS_HADOOP_HOME = Path.home() / "Downloads" / "winutils-master" / "hadoop-3.0.0"
```

### Si tu carpeta es diferente

Tienes dos opciones.

### Opcion A: configurar variable de entorno temporal en PowerShell

Antes de ejecutar el pipeline, define `HADOOP_HOME` apuntando a la carpeta que contiene `bin\winutils.exe`:

```powershell
$env:HADOOP_HOME = "D:\herramientas\hadoop-3.0.0"
$env:PATH = "$env:HADOOP_HOME\bin;$env:PATH"
.\.venv\Scripts\python.exe -m src.run_pipeline
```

Ejemplo si lo tienes en otra carpeta de Descargas:

```powershell
$env:HADOOP_HOME = "C:\Users\chris\Downloads\otra-carpeta\hadoop-3.0.0"
$env:PATH = "$env:HADOOP_HOME\bin;$env:PATH"
```

### Opcion B: configurar variable de entorno permanente en Windows

1. Abrir "Editar las variables de entorno del sistema".
2. Entrar en "Variables de entorno".
3. Crear o editar la variable de usuario:

```text
HADOOP_HOME=C:\ruta\a\hadoop-3.0.0
```

4. Editar `Path` y agregar:

```text
%HADOOP_HOME%\bin
```

5. Cerrar y volver a abrir VS Code o PowerShell.

### Como validar

```powershell
Test-Path "$env:HADOOP_HOME\bin\winutils.exe"
```

Debe devolver:

```text
True
```

Si devuelve `False`, corrige la ruta antes de ejecutar Spark.

### Nota para otros equipos

Si otra persona clona el proyecto, no debe cambiar el codigo si no quiere. Basta con definir `HADOOP_HOME` en su maquina. El codigo solo usa la ruta por defecto de Descargas cuando no encuentra `HADOOP_HOME` ya configurado.
