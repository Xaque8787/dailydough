import re
from sqlalchemy.orm import Session

def create_slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text

def ensure_unique_slug(db: Session, model, base_slug: str, exclude_id: int = None) -> str:
    slug = base_slug
    counter = 1

    while True:
        query = db.query(model).filter(model.slug == slug)
        if exclude_id:
            query = query.filter(model.id != exclude_id)

        if not query.first():
            return slug

        slug = f"{base_slug}-{counter}"
        counter += 1
