import requests
import json
import time

URL = "http://localhost:8000/predict"

# Los 10 casos de prueba definidos en la propuesta de proyecto
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
    {"input": "Civilization VI", "platform": "Windows", "expected": "Humankind"}
]

def run_evaluation():
    print("=" * 80)
    print("EJECUTANDO EVALUACIÓN AUTOMATIZADA DE CALIDAD (10 CASOS)")
    print("=" * 80)
    
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
                    
                    # 1. Cargar catálogo de referencia en el test
                    try:
                        with open("data/steam_clean.json", "r", encoding="utf-8") as fdb:
                            db_games = json.load(fdb)
                    except:
                        db_games = []
                        
                    # Buscar juego de entrada y recomendado en DB
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
                        print(f"[{idx}/10] Caso: {case['input']} ({case['platform']}) -> Recomendado: '{output}' | Estado: {status} ({dt_ms}ms)")
                    else:
                        fail_count += 1
                        status = "FAIL"
                        print(f"[{idx}/10] Caso: {case['input']} ({case['platform']}) -> Recomendado: '{output}' | Estado: {status} ({dt_ms}ms) - NOTA: {reason_fail}")
                        
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
                    print(f"[{idx}/10] Caso: {case['input']} ({case['platform']}) -> ERROR API: {error_msg}")
            else:
                fail_count += 1
                print(f"[{idx}/10] Caso: {case['input']} ({case['platform']}) -> ERROR HTTP {response.status_code}")
                
        except Exception as e:
            fail_count += 1
            print(f"[{idx}/10] Caso: {case['input']} ({case['platform']}) -> ERROR CONEXIÓN: {str(e)}")
            
    print("=" * 80)
    print("RESUMEN DE LA EVALUACIÓN:")
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
    
    # Guardar reporte de resultados
    with open("tests/eval_report.json", "w", encoding="utf-8") as f:
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
        print("Reporte de evaluación guardado en: 'tests/eval_report.json'")

if __name__ == "__main__":
    run_evaluation()
