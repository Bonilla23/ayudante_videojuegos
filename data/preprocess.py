import csv
import json
import os

# Rutas relativas con ../ desde el directorio del script para máxima portabilidad
CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/steam.csv")
JSON_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/steam_clean.json")

def preprocess():
    print("Iniciando preprocesamiento de steam.csv...")
    if not os.path.exists(CSV_PATH):
        print(f"Error: No se encuentra el archivo en {CSV_PATH}")
        return

    processed_games = []

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                name = row["name"].strip()
                platforms_raw = row["platforms"].strip().lower()
                categories_raw = row["categories"].strip()
                genres_raw = row["genres"].strip()
                
                pos = int(row["positive_ratings"])
                neg = int(row["negative_ratings"])
                total_ratings = pos + neg

                # Filtrar juegos con menos de 100 valoraciones totales para eliminar títulos irrelevantes/basura
                if total_ratings < 100:
                    continue

                # Calcular un rating de 1 a 10
                rating = round((pos / total_ratings) * 10, 2) if total_ratings > 0 else 0.0

                # Formatear campos
                # Las plataformas vienen separadas por punto y coma (windows;mac;linux)
                # Las convertimos en una lista limpia capitalizada
                platforms_map = {"windows": "Windows", "mac": "Mac", "linux": "Linux"}
                platforms = [platforms_map[p] for p in platforms_raw.split(";") if p in platforms_map]
                
                genres = [g.strip() for g in genres_raw.split(";") if g.strip()]
                categories = [c.strip() for c in categories_raw.split(";") if c.strip()]
                
                # Una descripción corta simulada a partir de los tags e información básica si no existe columna de descripción
                short_desc = f"Un aclamado juego de {genres[0]} desarrollado por {row['developer']}."
                
                processed_games.append({
                    "name": name,
                    "genres": genres,
                    "categories": categories,
                    "platforms": platforms,
                    "rating": rating,
                    "short_description": short_desc
                })
            except Exception as e:
                # Omitir filas defectuosas
                continue

    # Guardar en el archivo de salida
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_games, f, indent=2, ensure_ascii=False)

    print(f"Completado! Se han procesado y guardado {len(processed_games)} juegos en: '{JSON_OUTPUT_PATH}'")

if __name__ == "__main__":
    preprocess()
