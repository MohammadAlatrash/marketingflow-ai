from marketingflow.graph import graph

state = {
    "client": {
        "business_name": "FitZone",
        "industry": "Fitness",
        "products_services": "Online fitness coaching",
        "target_audience": "Busy professionals aged 25-40",
        "goal": "Generate leads",
        "platforms": "Instagram and Facebook",
        "tone": "Friendly and motivating",
        "special_offers": "Free first consultation",
        "extra_knowledge": "No instant-result claims. Focus on sustainable habits.",
    },
    "request": "Create a complete 7-day marketing campaign with ready-to-publish content.",
    "duration_days": 7,
}

result = graph.invoke(state)
print(result["final_output"])
