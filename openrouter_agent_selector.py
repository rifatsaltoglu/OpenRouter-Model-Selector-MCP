from mcp.server.fastmcp import FastMCP
import requests
import re

mcp = FastMCP("OpenRouter Agent Selector")

CATEGORIES = {
    "image-understanding": ["fotoğraf analiz", "görsel analiz", "resmi yorumla", "image analysis", "image understanding"],
    "video-understanding": ["video analiz", "video understanding", "videoyu anla"],
    "transcription": ["transkript", "ses yazıya", "speech to text", "stt"],
    "speech": ["seslendirme", "metni sese", "text to speech", "tts"],
    "image-generation": ["görsel oluşturma", "resim üret", "image generation", "fotoğraf oluştur"],
    "video-generation": ["video oluşturma", "video generation", "video üret"]
}

def determine_category(topic):
    topic_lower = topic.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in topic_lower for kw in keywords):
            return cat
    return "text"

def fetch_models(category):
    url = "https://openrouter.ai/api/v1/models"
    if category == "transcription":
        url += "?output_modalities=transcription"
    elif category == "speech":
        url += "?output_modalities=speech"
    elif category == "image-generation":
        url += "?output_modalities=image"
    elif category == "video-generation":
        url += "?output_modalities=video"
    
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("data", [])

def get_cost(model):
    pricing = model.get("pricing", {})
    if pricing is None:
        return -1.0
    try:
        p = float(pricing.get("prompt", 0))
        c = float(pricing.get("completion", 0))
        i = float(pricing.get("image_output", 0))
        
        # openrouter fusion (ve benzeri dinamik modeller) -1 dönebiliyor
        if p < 0 or c < 0 or i < 0:
            return -1.0
            
        return p + c + i
    except (ValueError, TypeError):
        return -1.0

def get_benchmark(model, category):
    bench = model.get("benchmarks", {})
    if not bench:
        return None
    
    aa = bench.get("artificial_analysis", {})
    if aa and aa.get("intelligence_index") is not None:
        return float(aa["intelligence_index"])
    
    da = bench.get("design_arena", [])
    if da:
        cat_matches = []
        if category == "text":
            cat_matches = [item for item in da if item.get("category", "") in ["codecategories", "fullstack", "webapps"]]
        
        if not cat_matches:
            cat_matches = da
            
        if cat_matches:
            return max([float(item.get("elo", 0)) for item in cat_matches])
            
    return None

def star_rating(val, min_val, max_val, is_price=False):
    if val is None or val < 0:
        return "N/A"
    if max_val == min_val:
        stars = 3
    else:
        score = (val - min_val) / (max_val - min_val)
        stars = int(round(1 + score * 4))
        stars = max(1, min(5, stars))
        
    star_str = "★" * stars + "☆" * (5 - stars)
    
    # Textual description
    if is_price:
        if stars == 5: text = " (High Price)"
        elif stars == 4: text = " (Above Average Price)"
        elif stars == 3: text = " (Average Price)"
        elif stars == 2: text = " (Low Price)"
        else: text = " (Very Low Price)"
    else:
        if stars == 5: text = " (High Performance)"
        elif stars == 4: text = " (Above Average Performance)"
        elif stars == 3: text = " (Average Performance)"
        elif stars == 2: text = " (Low Performance)"
        else: text = " (Very Low Performance)"
        
    return star_str + text

@mcp.tool()
def select_best_agent(topic: str) -> str:
    """
    Kullanıcının konusuna göre en iyi OpenRouter ajanlarını bulur, filtreler ve fiyat ile benchmarka göre (1-5 yıldız arası) puanlayıp listeler.
    """
    try:
        cat = determine_category(topic)
        models = fetch_models(cat)
        
        if cat == "image-understanding":
            models = [m for m in models if "image" in m.get("architecture", {}).get("input_modalities", [])]
        elif cat == "video-understanding":
            models = [m for m in models if "video" in m.get("architecture", {}).get("input_modalities", [])]
        elif cat == "text":
            topic_words = set(re.findall(r'\w+', topic.lower()))
            if len(topic_words) > 0:
                filtered_models = []
                for m in models:
                    text_to_search = (m.get("name", "") + " " + m.get("description", "")).lower()
                    if topic.lower() in text_to_search or any(w in text_to_search for w in topic_words if len(w) > 3):
                        filtered_models.append(m)
                
                # Eğer çok fazla elenmişse, tüm modelleri dönerek fallback yap
                if len(filtered_models) > 0:
                    models = filtered_models

        if not models:
            return f"No matching models found for this topic ('{topic}')."
            
        for m in models:
            m["_cost"] = get_cost(m)
            m["_bench"] = get_benchmark(m, cat)
            
        valid_costs = [m["_cost"] for m in models if m["_cost"] >= 0]
        min_cost = min(valid_costs) if valid_costs else 0
        max_cost = max(valid_costs) if valid_costs else 0
        
        valid_bench = [m["_bench"] for m in models if m["_bench"] is not None]
        min_bench = min(valid_bench) if valid_bench else 0
        max_bench = max(valid_bench) if valid_bench else 0

        # En pahalıya 5 yıldız vereceğimiz için maliyet listesini maliyete göre AZALAN sırada diziyoruz.
        models.sort(key=lambda x: x["_cost"], reverse=True)
        
        cat_emojis = {
            "image-understanding": "👁️ Image Understanding",
            "video-understanding": "📼 Video Understanding",
            "transcription": "🎤 STT (Transcription)",
            "speech": "🗣️ TTS (Text-to-Speech)",
            "image-generation": "🎨 Image Generation",
            "video-generation": "🎬 Video Generation",
            "text": "📝 Text / Coding"
        }
        cat_display = cat_emojis.get(cat, cat)
        
        output = [f"### 🤖 Recommended Models for '{topic}' ({cat_display})\n"]
        
        for m in models[:10]: 
            c_stars = "variable/N/A" if m["_cost"] < 0 else star_rating(m["_cost"], min_cost, max_cost, is_price=True)
            b_stars = "N/A" if m["_bench"] is None else star_rating(m["_bench"], min_bench, max_bench, is_price=False)
            
            desc = m.get("description", "")
            if desc:
                desc = desc.split(". ")[0].strip()
                if not desc.endswith("."):
                    desc += "."
            else:
                desc = "No description available."
                
            output.append(f"- **{m['name']}**\n  - Price: {c_stars}\n  - Benchmark: {b_stars}\n  - Description: {desc}\n")
            
        return "\n".join(output)

    except requests.RequestException as e:
        return f"A network error occurred while connecting to OpenRouter API: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    mcp.run()
