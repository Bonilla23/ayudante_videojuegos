import json
import math
import os

LOG_PATH = "logs/logs.jsonl"

def calculate_percentiles():
    if not os.path.exists(LOG_PATH):
        print(f"Error: No se encontró el archivo de logs en '{LOG_PATH}'.")
        return

    latencies = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    if "latency_ms" in data:
                        latencies.append(data["latency_ms"])
                except json.JSONDecodeError:
                    continue

    if not latencies:
        print("No se encontraron registros de latencia en el archivo de logs.")
        return

    # Ordenar las latencias de menor a mayor
    latencies.sort()
    n = len(latencies)

    # Función para calcular percentiles por interpolación lineal (equivalente a numpy)
    def get_percentile(data, percentile):
        if not data:
            return 0
        k = (len(data) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        d0 = data[int(f)] * (c - k)
        d1 = data[int(c)] * (k - f)
        return d0 + d1

    p50 = get_percentile(latencies, 50)
    p95 = get_percentile(latencies, 95)

    print("=" * 60)
    print("ANÁLISIS DE RENDIMIENTO (LATENCIA)")
    print("=" * 60)
    print(f"Archivo analizado: {LOG_PATH}")
    print(f"Número total de peticiones (N): {n}")
    print(f"Latencia Mínima: {latencies[0]} ms ({latencies[0]/1000:.2f} s)")
    print(f"Latencia Máxima: {latencies[-1]} ms ({latencies[-1]/1000:.2f} s)")
    print("-" * 60)
    print(f"p50 (Mediana): {p50:.1f} ms ({p50/1000:.2f} s)")
    print(f"p95 (Percentil 95): {p95:.1f} ms ({p95/1000:.2f} s)")
    print("=" * 60)
    print("\n¿Qué significan estos números?")
    print(f" - p50: El 50% de tus usuarios experimentaron una latencia de {p50/1000:.2f} s o menor (caso típico).")
    print(f" - p95: El 95% de tus usuarios experimentaron una latencia de {p95/1000:.2f} s o menor (caso adverso común).")
    print("=" * 60)

if __name__ == "__main__":
    calculate_percentiles()
