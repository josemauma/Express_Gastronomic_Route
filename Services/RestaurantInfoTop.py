import math
import re

class TopRestaurantsExtractor:
    def __init__(self, restaurants_json):
        self.restaurants = restaurants_json

    @staticmethod
    def compute_score(rating, num_reviews):
        if rating is None or num_reviews is None:
            return -1
        return rating * math.log10(num_reviews + 1)

    def format_opening_hours(self,hours_list):
        formatted = []
        for h in hours_list:
            # Quita espacios raros y guiones unicode
            clean = (h.replace('\u2009', ' ')
                    .replace('\u2013', '-')
                    .replace('\u2014', '-')
                    .replace('–', '-')
                    .replace('—', '-')
                    .replace('‑', '-')
                    .replace('\u202f', ' '))
            # Separa los días y las horas
            match = re.match(r"^(\w+):\s*([0-9]{1,2}:[0-9]{2}\s*[APMapm]{2})\s*[-–—]?\s*([0-9]{1,2}:[0-9]{2}\s*[APMapm]{2})", clean.replace(" ", ""))
            if match:
                day = match.group(1)
                open_hour = match.group(2)
                close_hour = match.group(3)
                # Inserta espacio antes de AM/PM si falta
                open_hour = re.sub(r'([0-9])([APMapm]{2})$', r'\1 \2', open_hour)
                close_hour = re.sub(r'([0-9])([APMapm]{2})$', r'\1 \2', close_hour)
                formatted.append(f"- {day}: {open_hour} - {close_hour}")
            else:
                # Como fallback, intenta poner espacios entre números y AM/PM y guiones
                temp = re.sub(r'(\d{1,2}:\d{2})([APMapm]{2})', r'\1 \2', clean)
                temp = temp.replace("AM-", "AM - ").replace("PM-", "PM - ")
                formatted.append(f"- {temp.strip()}")
        return formatted


    def get_top_3(self, n=3):
        desired_fields = [
            'name', 'formatted_address', 'formatted_phone_number', 'website',
            'opening_hours', 'current_opening_hours', 'rating', 'user_ratings_total',
            'reviews', 'price_level', 'wheelchair_accessible_entrance', 'delivery',
            'dine_in', 'takeout', 'reservable'
        ]
    # 1. Calcula todos los scores originales
        all_scores = []
        for r in self.restaurants:
            rating = r.get("rating")
            num_reviews = r.get("user_ratings_total")
            score = self.compute_score(rating, num_reviews)
            all_scores.append((score, r))
        # Filtra solo los válidos
        all_scores = [r for r in all_scores if r[0] >= 0]
        if not all_scores:
            return []
        # 2. Normaliza los scores a 0-10
        min_score = min(s for s, _ in all_scores)
        max_score = max(s for s, _ in all_scores)
        # Evita división por cero
        if max_score == min_score:
            norm = lambda s: 10.0
        else:
            norm = lambda s: 10 * (s - min_score) / (max_score - min_score)
        # 3. Aplica normalización y ordena
        ranked = []
        for score, r in all_scores:
            score_norm = norm(score)
            ranked.append((score_norm, r))
        ranked.sort(reverse=True, key=lambda x: x[0])
        top_n = ranked[:n]
        minimal = []
        for score, r in top_n:
            info = {
                "name": r.get("name"),
                "address": r.get("formatted_address"),
                "phone_number": r.get("formatted_phone_number"),
                "wheelchair_accessible_entrance": r.get("wheelchair_accessible_entrance", False),
                "takeout": r.get("takeout", False),
                "price_level": r.get("price_level", -1),
                "delivery": r.get("delivery", False),
                "reservable": r.get("reservable", False),
                
                "score": round(score, 2),  # Score normalizado 0-10, ¡y todos diferentes!
                "opening_hours": self.format_opening_hours(r.get("opening_hours", {}).get("weekday_text", [])),
                "reviews": [
                    {
                        "author_name": rev.get("author_name"),
                        "rating": rev.get("rating"),
                        "text": rev.get("text"),
                        "time": rev.get("time"),
                    }
                    for rev in sorted(r.get("reviews", []), key=lambda x: x.get("time", 0), reverse=True)[:2]
                ]
            }
            minimal.append(info)
        return minimal

        """ 
        save_top_n_json(self, input_filename, n=3):
        minimal = self.get_top_n_minimal(n)
        # Añade el sufijo -topN antes de la extensión
        base, ext = os.path.splitext(input_filename)
        output_filename = f"{base}-top{n}{ext}"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(minimal, f, ensure_ascii=False, indent=2)
        print(f"Archivo guardado: {output_filename}")

        """
    