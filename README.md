# Open source recommendation engine

# Rekky is an open source item similarity & collaborative filtering recommendation engine

---

- Calculates items similarity vectors via the OpenAI embeddings API
- Uses Qdrant to store & search items with similar vectors
- Uses Elasticsearch for collaborative filtering recommendations
- [TODO] Automatically mixes collaborative with similarity recommendations when collaborative data are not enough to provide good recommendations

## Running locally

1. Copy the .env.example to .env and add your OpenAI api key
    
    `cp .env.example .env`
    
2. Run docker compose
    
    `docker compose up`
    
3. Optionaly add the movielens dataset for experimentation
    
    `python scripts/load_movielens_dataset.py -d small`
    

## API usage

---

### Ingesting items (for similarity recommendations)

You can send up to 100.000 items in a single post request, the ingestion happens asyncronously via celery tasks. 

```python
requests.post("/api/items", json={
    "collection": "movies",
    "items": [
        {
            "id": "1",
            "properties": {
                "genre": [
                    "Adventure",
                    "Animation"
                ],
                "name": "SpongeBob SquarePants Movie, The (2004)"
            }
        },
        {
            "id": "2",
            "properties": {
                "genre": [
                    "Action"
                ],
                "name": "Matrix"
            }
        }
    ]
})
```

### Getting recommendations from similarity

```python
requests.post("/api/recommend", json={
    "collection": "movies",
    "config": {
        "similarity": {
            "similar_to_item": "1" ## similar to item with id=1
        }
    }
})

## OR

requests.post("/api/recommend", json={
    "collection": "movies",
    "config": {
        "similarity": {
            "similar_to_properties": {
                "name": "animation"
            }
        }
    }
})
```

### Ingesting events (for collaborative filtering recommendations)

You can send up to 1 million events in a single post request, the ingestion happens asyncronously via celery tasks. 

```python
requests.post("/api/events", json={
    "collection": "movies",
    "events": [
        {
            "item_id": "1",
            "user_id": "3112779531605195",
            "event": "movie_like"
        },
        {
            "item_id": "2",
            "user_id": "3JAV8WT10U1FF49I",
            "event": "movie_like"
        },
        {
            "item_id": "1",
            "user_id": "EUI3UD9KLLPS9WZ8",
            "event": "movie_like"
        }
    ]
})
```

### Getting recommendations from collaborative filtering

```python
requests.post("/api/recommend", json={
    "collection": "movies",
    "config": {
        "collaborative": {
            "item_ids": ["1"]
        }
    }
})
```