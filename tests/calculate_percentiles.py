import json
import math
import os

LOG_PATH = "logs/logs.jsonl"

def get_percentile(data, percentile):
    """Calcula el percentil usando interpolación lineal (estilo NumPy)."""
    if not data:
        return 0
    # Importante: los datos deben estar ordenados para calcular percentiles correctamente
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1

def print_metrics_block(latencies, label):
    """Imprime un bloque estético de métricas para un conjunto de latencias."""
    n = len(latencies)
    if n == 0:
        print(f"\n[!] No hay datos para el segmento: {label}")
        return

    # Usar una copia ordenada para estadísticas
    sorted_l = sorted(latencies)
    p50 = get_percentile(sorted_l, 50)
    p95 = get_percentile(sorted_l, 95)
    avg = sum(latencies) / n

    print(f"\n>>> ANÁLISIS: {label.upper()}")
    print("-" * 65)
    print(f" Muestras Analizadas: {n}")
    print(f" Latencia Mínima:    {sorted_l[0]:>7.1f} ms | {sorted_l[0]/1000:>5.2f} s")
    print(f" Latencia Máxima:    {sorted_l[-1]:>7.1f} ms | {sorted_l[-1]/1000:>5.2f} s")
    print(f" Latencia Media:     {avg:>7.1f} ms | {avg/1000:>5.2f} s")
    print(f" p50 (Mediana):      {p50:>7.1f} ms | {p50/1000:>5.2f} s")
    print(f" p95 (Percentil 95): {p95:>7.1f} ms | {p95/1000:>5.2f} s")
    print("-" * 65)

def calculate_percentiles():
    if not os.path.exists(LOG_PATH):
        print(f"Error: No se encontró el archivo de logs en '{LOG_PATH}'.")
        return

    all_latencies = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        # Solo procesar latencias de peticiones que NO sean errores
                        if "latency_ms" in data and data.get("status") != "ERROR":
                            all_latencies.append(data["latency_ms"])
                    except json.JSONDecodeError:
                        continue

    if not all_latencies:
        print("No se encontraron registros de latencia en el archivo de logs.")
        return

    print("=" * 65)
    print("      📊 INFORME DE RENDIMIENTO MULTI-BLOQUE (LATENCIA) 📊")
    print("=" * 65)
    print(f"Archivo de origen: {LOG_PATH}")
    print(f"Carga total detectada: {len(all_latencies)} registros")

    # Los tres bloques solicitados por el usuario: 5, 10 y 22 pruebas
    for count in [5, 10, 22]:
        if count <= len(all_latencies):
            subset = all_latencies[:count]
            print_metrics_block(subset, f"{count} pruebas")
        else:
            print(f"\n[!] Saltando bloque de {count}: Solo hay {len(all_latencies)} registros.")

    print("\n" + "=" * 65)
    print("GLOSARIO DE MÉTRICAS:")
    print(" - p50: El 50% de las peticiones tardaron menos de este tiempo.")
    print(" - p95: Caso de borde crítico. El 95% de las llamadas son más veloces.")
    print("-" * 65)
    print(" Informe generado exitosamente.")
    print("=" * 65)

if __name__ == "__main__":
    calculate_percentiles()

