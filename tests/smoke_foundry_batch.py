import requests
import json
import time

URL = "http://localhost:8000/predict"

test_cases = [
    {"input": "Half-Life", "platform": "Windows"},
    {"input": "Portal 2", "platform": "Mac"},
    {"input": "Left 4 Dead 2", "platform": "Linux"},
    {"input": "Hollow Knight", "platform": "Mac"},
    {"input": "Forza Horizon 5", "platform": "Windows"},
    {"input": "Age Of Empires II", "platform": "Linux"},
    {"input": "Skyrim", "platform": "Windows"},
    {"input": "Stardew Valley", "platform": "Windows"},
    {"input": "Civilization VI", "platform": "Windows"}
]

def run_batch_test():
    print(f"{'INPUT':<20} | {'PLATAFORMA':<10} | {'RECOMENDACIÓN':<25} | {'MOTIVO'}")
    print("-" * 100)
    
    for case in test_cases:
        payload = {
            "input": case["input"],
            "platform": case["platform"],
            "options": {"temperature": 0.2, "max_tokens": 600}
        }
        
        try:
            response = requests.post(URL, json=payload, timeout=15)
            data = response.json()
            
            if data.get("ok"):
                juego = data.get("output", "N/A")
                motivo = data.get("motivo", "N/A")
                print(f"{case['input']:<20} | {case['platform']:<10} | {juego:<25} | {motivo}")
            else:
                print(f"{case['input']:<20} | {case['platform']:<10} | ERROR: {data.get('error')}")
                
        except Exception as e:
            print(f"{case['input']:<20} | {case['platform']:<10} | ERROR CONEXIÓN: {str(e)}")
        
        # Esperar a que el usuario pulse Enter para el siguiente caso
        input("\n--- Presiona Enter para el siguiente caso ---")

if __name__ == "__main__":
    run_batch_test()
