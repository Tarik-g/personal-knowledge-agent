"""Run one real multilingual embedding search without a database."""

from jarvis.embeddings import LocalEmbeddingModel
from jarvis.retrieval import find_relevant_chunks

chunks = [
    {
        "dateiname": "beispiel.pdf",
        "seitenzahl": 1,
        "abschnitt_nummer": 1,
        "text": "Das Fahrzeug muss wegen eines Motorschadens in die Werkstatt.",
    },
    {
        "dateiname": "beispiel.pdf",
        "seitenzahl": 2,
        "abschnitt_nummer": 1,
        "text": "Für den Kuchen werden Mehl, Butter und Zucker vermischt.",
    },
    {
        "dateiname": "beispiel.pdf",
        "seitenzahl": 3,
        "abschnitt_nummer": 1,
        "text": "Der Urlaub beginnt mit einer Zugfahrt nach Hamburg.",
    },
]

question = "Warum muss das Auto repariert werden?"
results = find_relevant_chunks(question, chunks, LocalEmbeddingModel(), limit=3)

print(f"Frage: {question}\n")
for result in results:
    print(
        f"{result['aehnlichkeit']:.3f} | Seite {result['seitenzahl']} | "
        f"{result['text']}"
    )
