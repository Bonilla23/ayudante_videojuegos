import requests
import json
import time

URL = "http://localhost:8000/predict"

# 25 casos de prueba para el Checkpoint de Calidad (objetivo 25)
TEST_CASES = [
    {"input": "Counter Strike", "platform": "Linux", "expected": "Team Fortress Classic"},
    {"input": "Half-Life", "platform": "Windows", "expected": "Quake"},
    {"input": "Portal 2", "platform": "Mac", "expected": "The Talos Principle"},
    {"input": "Left 4 Dead 2", "platform": "Linux", "expected": "Warhammer: Vermintide 2"},
    {"input": "Hollow Knight", "platform": "Mac", "expected": "Celeste"},
    {"input": "Forza Horizon 5", "platform": "Windows", "expected": "Dirt 5"},
    {"input": "Age Of Empires II", "platform": "Linux", "expected": "0 A.D."},
    {"input": "Skyrim", "platform": "Windows", "expected": "Dragon's Dogma"},
    {"input": "Stardew Valley", "platform": "Windows", "expected": "Terraria"},
    {"input": "Civilization VI", "platform": "Windows", "expected": "Humankind"},
    {"input": "Half-Life 2", "platform": "Windows", "expected": "Half-Life"},
    {"input": "Team Fortress 2", "platform": "Linux", "expected": "Counter-Strike: Source"},
    {"input": "Dota 2", "platform": "Mac", "expected": "Left 4 Dead 2"},
    {"input": "Killing Floor", "platform": "Windows", "expected": "Red Orchestra: Ostfront 41-45"},
    {"input": "Darwinia", "platform": "Linux", "expected": "Uplink"},
    {"input": "Uplink", "platform": "Mac", "expected": "DEFCON"},
    {"input": "DEFCON", "platform": "Windows", "expected": "Multiwinia"},
    {"input": "Disciples II: Rise of the Elves", "platform": "Windows", "expected": "Disciples II: Gallean's Return"},
    {"input": "Arx Fatalis", "platform": "Windows", "expected": "Dark Messiah of Might & Magic"},
    {"input": "Costume Quest", "platform": "Windows", "expected": "Costume Quest 2"},
    {"input": "Left 4 Dead", "platform": "Mac", "expected": "Left 4 Dead 2"},
    {"input": "Portal", "platform": "Linux", "expected": "Portal 2"},
    {"input": "Space Empires IV Deluxe", "platform": "Windows", "expected": "Space Empires V"},
    {"input": "Red Orchestra: Ostfront 41-45", "platform": "Linux", "expected": "Killing Floor"},
    {"input": "Counter-Strike: Condition Zero", "platform": "Mac", "expected": "Counter-Strike"}
]

def run_evaluation():
    print("=" * 80)
    print(f"EJECUTANDO EVALUACIÓN AUTOMATIZADA EXTENDIDA ({len(TEST_CASES)} CASOS)")
    print("=" * 80)
    
    # Cargar catálogo de referencia una sola vez al inicio para optimizar rendimiento
    try:
        with open("data/steam_clean.json", "r", encoding="utf-8") as fdb:
            db_games = json.load(fdb)
        print(f"Catálogo de referencia cargado ({len(db_games)} juegos) con éxito.\n")
    except Exception as e:
        print(f"WARNING: No se pudo cargar catálogo de referencia: {e}\n")
        db_games = []

    ok_count = 0
    fail_count = 0
    total_latency = 0
    
    results = []
    
    for idx, case in enumerate(TEST_CASES, 1):
        payload = {
            "input": case["input"],
            "platform": case["platform"],
            "options": {"temperature": 0.2, "max_tokens": 256}
        }
        
        t0 = time.time()
        try:
            response = requests.post(URL, json=payload, timeout=15)
            dt_ms = int((time.time() - t0) * 1000)
            total_latency += dt_ms
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    output = data.get("output", "")
                    motivo = data.get("motivo", "")
                    meta = data.get("meta", {})
                    provider = meta.get("provider", "unknown")
                    
                    # --- VALIDACIÓN DINÁMICA DE MÉTRICA REAL ---
                    is_ok = False
                    reason_fail = ""
                    
                    # Buscar juego de entrada y recomendado en la DB precargada
                    game_in = next((g for g in db_games if case["input"].lower() in g["name"].lower()), None)
                    game_out = next((g for g in db_games if output.lower() in g["name"].lower()), None)
                    
                    if not game_out:
                        reason_fail = "Juego recomendado no existe en catálogo"
                    elif case["platform"] not in game_out["platforms"]:
                        reason_fail = f"Incompatible con {case['platform']}"
                    elif game_in and not set(game_in["genres"]).intersection(set(game_out["genres"])):
                        reason_fail = "No comparte género principal"
                    else:
                        is_ok = True
                    # --------------------------------------------
                    
                    if is_ok:
                        ok_count += 1
                        status = "OK"
                        print(f"[{idx}/{len(TEST_CASES)}] Caso: {case['input']} ({case['platform']}) -> Recomendado: '{output}' | Estado: {status} ({dt_ms}ms)")
                    else:
                        fail_count += 1
                        status = "FAIL"
                        print(f"[{idx}/{len(TEST_CASES)}] Caso: {case['input']} ({case['platform']}) -> Recomendado: '{output}' | Estado: {status} ({dt_ms}ms) - NOTA: {reason_fail}")
                        
                    results.append({
                        "id": idx,
                        "input": case["input"],
                        "platform": case["platform"],
                        "expected": case["expected"],
                        "output": output,
                        "motivo": motivo,
                        "status": status,
                        "latency_ms": dt_ms,
                        "provider": provider,
                        "note": reason_fail if not is_ok else "Pasa métrica de calidad"
                    })
                else:
                    fail_count += 1
                    error_msg = data.get("error", {}).get("message", "Error desconocido")
                    print(f"[{idx}/{len(TEST_CASES)}] Caso: {case['input']} ({case['platform']}) -> ERROR API: {error_msg}")
                    results.append({
                        "id": idx,
                        "input": case["input"],
                        "platform": case["platform"],
                        "expected": case["expected"],
                        "output": "ERROR",
                        "motivo": f"API Error: {error_msg}",
                        "status": "ERROR_API",
                        "latency_ms": dt_ms,
                        "provider": "unknown",
                        "note": error_msg
                    })
            else:
                fail_count += 1
                print(f"[{idx}/{len(TEST_CASES)}] Caso: {case['input']} ({case['platform']}) -> ERROR HTTP {response.status_code}")
                results.append({
                    "id": idx,
                    "input": case["input"],
                    "platform": case["platform"],
                    "expected": case["expected"],
                    "output": "ERROR",
                    "motivo": f"HTTP {response.status_code}",
                    "status": "ERROR_HTTP",
                    "latency_ms": dt_ms,
                    "provider": "unknown",
                    "note": f"Status code: {response.status_code}"
                })
                
        except Exception as e:
            fail_count += 1
            print(f"[{idx}/{len(TEST_CASES)}] Caso: {case['input']} ({case['platform']}) -> ERROR CONEXIÓN: {str(e)}")
            results.append({
                "id": idx,
                "input": case["input"],
                "platform": case["platform"],
                "expected": case["expected"],
                "output": "ERROR",
                "motivo": "Excepción de conexión o ejecución",
                "status": "ERROR_CONNECTION",
                "latency_ms": 0,
                "provider": "unknown",
                "note": str(e)
            })
            
    print("=" * 80)
    print("RESUMEN DE LA EVALUACIÓN EXTENDIDA:")
    print("=" * 80)
    total = ok_count + fail_count
    precision = (ok_count / total * 100) if total > 0 else 0
    avg_latency = (total_latency / total) if total > 0 else 0
    
    print(f"Total Casos: {total}")
    print(f"Aprobados (OK): {ok_count}")
    print(f"Fallidos (FAIL): {fail_count}")
    print(f"Precisión: {precision:.1f}%")
    print(f"Latencia Media: {avg_latency:.1f} ms")
    print("=" * 80)
    
    # Guardar reporte de resultados extendido
    with open("tests/eval_report_extended.json", "w", encoding="utf-8") as f:
        json.dump({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "summary": {
                "total": total,
                "ok": ok_count,
                "fail": fail_count,
                "precision_percent": precision,
                "avg_latency_ms": avg_latency
            },
            "results": results
        }, f, indent=4, ensure_ascii=False)
        print("Reporte de evaluación guardado en: 'tests/eval_report_extended.json'")

if __name__ == "__main__":
    run_evaluation()
